import { useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import DataTable from "./table";

export default function SetResult() {
  const { state } = useLocation();
  const setData = state.data;
  const [selectedSetKey, setSelectedSetKey] = useState(Object.keys(setData)[0]);
  const [subsets, setSubsets] = useState([]);
  const [partitions, setPartitions] = useState([]);
  const [subsetOffset, setSubsetOffset] = useState(0);
  const [partOffset, setPartOffset] = useState(0);
  const [hasMoreSubset, setHasMoreSubset] = useState(false);
  const [hasMorePart, setHasMorePart] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTab, setSelectedTab] = useState("subset");
  const [isLoading, setIsLoading] = useState(false);
  const [subsetPageIndex, setSubsetPageIndex] = useState(0);
  const [partPageIndex, setPartPageIndex] = useState(0);
  const limit = 5000;

  const formatSubsetData = (data, dataType = "subset") => {
    let baseIndex = 0;
    if (!data || typeof data !== "object") {
      console.warn(`Invalid data for ${dataType}:`, data);
      return [];
    }

    if (dataType === "part") {
      if (!Array.isArray(data)) {
        console.warn("Invalid partitions data:", data);
        return [];
      }
      return data.map((item, index) => ({
        شماره: index + 1,
        نوع: `افراز ${index + 1}`,
        اعضا: Array.isArray(item) ? item.join(", ") : String(item || ""),
      }));
    }

    return Object.keys(data).flatMap((key, groupIndex) => {
      const group = data[key];
      if (!Array.isArray(group)) {
        console.warn(`Invalid subset group for key ${key}:`, group);
        return [];
      }

      const result = group.map((item, index) => ({
        شماره: baseIndex + index + 1,
        نوع: `${key}`,
        اعضا: Array.isArray(item) ? item.join(", ") : String(item || ""),
      }));

      baseIndex += group.length;
      return result;
    });
  };

  useEffect(() => {
    const sendRequestParsub = async () => {
      setIsLoading(true);
      try {
        setError(null);
        const offset = selectedTab === "subset" ? subsetOffset : partOffset;
        const response = await fetch("http://localhost:8000/api/set/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            func: "parsub",
            set: state.sets,
            key: selectedSetKey,
            offset: offset,
            limit: limit,
            type: selectedTab,
          }),
        });
        if (!response.ok) throw new Error(`خطا: ${response.status}`);
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        if (selectedTab === "subset") {
          setSubsets((prev) => [...prev, ...formatSubsetData(data.subset)]);
          setHasMoreSubset(data.has_more_subset);
        } else {
          setPartitions((prev) => [...prev, ...formatSubsetData(data.part, "part")]);
          setHasMorePart(data.has_more_part);
        }
      } catch (error) {
        setError(`خطا: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };
    sendRequestParsub();
  }, [selectedSetKey, subsetOffset, partOffset, selectedTab]);

  const loadMore = () => {
    if (selectedTab === "subset") {
      setSubsetOffset((prev) => prev + limit);
    } else {
      setPartOffset((prev) => prev + limit);
    }
  };

  const handlePageIndexChange = (pageIndex, tab) => {
    if (tab === "subset") {
      setSubsetPageIndex(pageIndex);
    } else if (tab === "part") {
      setPartPageIndex(pageIndex);
    }
  };

  const spinnerStyles = `
    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid rgba(255, 255, 255, 0.2);
      border-top: 4px solid #ffffff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 20px auto;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;

  return (
    <motion.div
      initial={{
        borderRadius: 32,
        opacity: 0,
        scale: 0.9,
        backdropFilter: "blur(24px) brightness(0.5)",
      }}
      animate={{
        opacity: 1,
        scale: 1,
        backdropFilter: "blur(8px) brightness(1)",
      }}
      exit={{ borderRadius: 32, opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.5 }}
      className="relative flex mx-auto gap-5 p-4 lg:max-w-[1024px] lg:top-30 top-50 rounded-4xl shadow-black/20 bg-blue-950/5 backdrop-blur-sm backdrop-brightness-200 w-full"
    >
      <style>{spinnerStyles}</style>
      <div className="hidden lg:inline-block ">
        <ul className="sets-button p-2 hidden lg:flex relative right-[0px] text-lg shadow-sm flex-wrap flex-col p-1 rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200">
          {Object.keys(setData).map((key) => (
            <li key={key} className="m-1">
              <button
                type="button"
                className="shadow-black/20 transition-all duration-500 text-white p-2 px-4 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 rounded-full disabled:bg-blue-950/50 disabled:scale-90"
                disabled={selectedSetKey === key}
                onClick={() => {
                  setSelectedSetKey(key);
                  setSubsets([]);
                  setPartitions([]);
                  setSubsetOffset(0);
                  setPartOffset(0);
                  setSubsetPageIndex(0);
                  setPartPageIndex(0);
                }}
              >
                {key}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="flex w-full gap-5 flex-col lg:flex-row items-center justify-center">
        <div>
          <ul className="sets-button p-2 relative right-[0px] text-lg shadow-sm flex lg:hidden p-1 rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200">
            {Object.keys(setData).map((key) => (
              <li key={key} className="m-1">
                <button
                  type="button"
                  className="shadow-black/20 transition-all duration-500 text-white p-2 px-4 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 rounded-full disabled:bg-blue-950/50 disabled:scale-90"
                  disabled={selectedSetKey === key}
                  onClick={() => {
                    setSelectedSetKey(key);
                    setSubsets([]);
                    setPartitions([]);
                    setSubsetOffset(0);
                    setPartOffset(0);
                    setSubsetPageIndex(0);
                    setPartPageIndex(0);
                  }}
                >
                  {key}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedSetKey}
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5 }}
            className="set text-lg lg:max-w-1/2 lg:min-w-1/2 shadow-sm flex flex-col gap-5 p-5 rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 w-full"
          >
            <div className="text-lg justify-center text-white items-center shadow-sm flex max-h-1/7 w-full gap-12 p-5 rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200">
              <span className="text-nowrap">نام مجموعه: {selectedSetKey}</span>
              <span className="overflow-x-auto text-nowrap inline-block max-w-1/3">
                اعضای مجموعه: {setData[selectedSetKey]["memb"]}
              </span>
              <span className="overflow-x-auto text-nowrap inline-block max-w-1/3">
                تعداد اعضای مجموعه: {setData[selectedSetKey]["number"]}
              </span>
            </div>
            <div className="w-full mx-auto lg:order-2 lg:h-auto rounded-3xl backdrop-blur-sm backdrop-brightness-200 shadow-sm shadow-black/20">
              <div className="mx-auto p-3 mt-3 justify-center mb-4 w-fit relative right-[0px] text-lg shadow-sm flex p-1 rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200">
                <button
                  type="button"
                  className="shadow-black/20 transition-all duration-500 text-white p-2 px-4 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 rounded-full disabled:bg-blue-950/50 disabled:scale-90"
                  disabled={selectedTab === "subset"}
                  onClick={() => setSelectedTab("subset")}
                >
                  <span>زیر مجموعه‌ها</span>
                </button>
                <button
                  type="button"
                  className="shadow-black/20 transition-all duration-500 text-white p-2 px-4 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 rounded-full disabled:bg-blue-950/50 disabled:scale-90"
                  disabled={selectedTab === "part"}
                  onClick={() => setSelectedTab("part")}
                >
                  <span>افرازها</span>
                </button>
              </div>
              <div className="flex justify-center my-5">
                <button
                  type="button"
                  className="shadow-black/20 rounded-full hover:scale-105 transition-all duration-500 text-white p-2 px-4 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 rounded-lg disabled:blur-xs disabled:scale-90"
                  onClick={loadMore}
                  disabled={
                    (selectedTab === "subset" && !hasMoreSubset) ||
                    (selectedTab === "part" && !hasMorePart)
                  }
                >
                  بارگذاری بیشتر
                </button>
              </div>
              <AnimatePresence mode="wait">
                {error && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-red-500 text-center"
                  >
                    {error}
                  </motion.div>
                )}
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex justify-center items-center"
                  >
                    <div className="spinner"></div>
                  </motion.div>
                )}
                {selectedTab === "subset" && subsets.length > 0 && (
                  <DataTable
                    data={subsets}
                    showDelete={false}
                    maxHeight={300}
                    defaultPageIndex={subsetPageIndex}
                    onPageIndexChange={(pageIndex) => handlePageIndexChange(pageIndex, "subset")}
                  />
                )}
                {selectedTab === "part" && partitions.length > 0 && (
                  <DataTable
                    data={partitions}
                    showDelete={false}
                    maxHeight={300}
                    defaultPageIndex={partPageIndex}
                    onPageIndexChange={(pageIndex) => handlePageIndexChange(pageIndex, "part")}
                  />
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </AnimatePresence>
        <div className="sets h-full text-lg shadow-sm flex flex-wrap lg:flex-nowrap gap-12 p-5 rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 w-full"></div>
      </div>
    </motion.div>
  );
}