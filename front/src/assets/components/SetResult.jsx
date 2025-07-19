import { useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import DataTable from "./table";

export default function SetResult() {
  const { state } = useLocation();
  const setData = state.data;
  const [selectedSetKey, setSelectedSetKey] = useState(Object.keys(setData)[0]);
  const [parsubData, setParsubData] = useState(null);
  const [error, setError] = useState(null);
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [selectedTab, setSelectedTab] = useState("subset");

  useEffect(() => {
    const timeout = setTimeout(() => setIsFirstLoad(false), 50);
    return () => clearTimeout(timeout);
  }, []);

  const formatSubsetData = (data, dataType = "subset") => {
    if (!data || typeof data !== "object") return [];
    return Object.keys(data).map((key, index) => ({
      شماره: index + 1,
      نوع: dataType === "part" ? `افراز ${index + 1} ` : `${key}`,
      اعضا: Array.isArray(data[key]) ? data[key].join(", ") : data[key],
    }));
  };

  useEffect(() => {
    const sendRequest = async () => {
      try {
        setError(null);
        setParsubData(null); 
        const response = await fetch("http://localhost:8000/api/set/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            func: "parsub",
            set: state.sets,
            key: selectedSetKey,
          }),
        });
        if (!response.ok) {
          throw new Error(`درخواست با وضعیت ${response.status} ناموفق بود`);
        }
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        setParsubData(data);
        console.log("API response:", data);
        console.log("Subset data:", data.subset);
        console.log("Formatted subset data:", formatSubsetData(data.subset));
      } catch (error) {
        console.error("خطا در ارسال درخواست:", error);
        setError(`خطا: ${error.message}`);
      }
    };

    sendRequest();
  }, [selectedSetKey]);

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
      exit={{
        borderRadius: 32,
        opacity: 0,
        scale: 0.9,
      }}
      transition={{ duration: 0.5 }}
      className="relative flex mx-auto gap-5 p-4 lg:max-w-[1024px] lg:top-30 top-50 lg:rounded-4xl shadow-black/20 bg-blue-950/5 backdrop-blur-sm backdrop-brightness-200 w-full"
    >
      <style>{spinnerStyles}</style>
      <div>
        <ul className="sets-button p-2 relative right-[0px] text-lg shadow-sm flex flex-wrap flex-col p-1 lg:rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200">
          {Object.keys(setData).map((key) => (
            <li key={key} className="m-1">
              <button
                type="button"
                className="shadow-black/20 transition-all duration-500 text-white p-2 px-4 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 rounded-full disabled:bg-blue-950/50 disabled:scale-90"
                disabled={selectedSetKey === key}
                onClick={() => setSelectedSetKey(key)}
              >
                {key}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="flex w-full gap-5">
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedSetKey}
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5 }}
            className="set text-lg max-w-1/2 min-w-1/2 shadow-sm flex flex-col gap-5 p-5 lg:rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 w-full"
          >
            <div className="text-lg text-white items-center shadow-sm flex max-h-1/7 w-full gap-12 p-5 lg:rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200">
              <span className="text-nowrap">نام مجموعه: {selectedSetKey}</span>
              <span className="overflow-x-auto text-nowrap inline-block max-w-1/3">
                اعضای مجموعه: {setData[selectedSetKey]["memb"]}
              </span>
              <span className="overflow-x-auto text-nowrap inline-block max-w-1/3">
                تعداد اعضای مجموعه: {setData[selectedSetKey]["number"]}
              </span>
            </div>
            <div className="w-full mx-auto p-4 lg:order-2 lg:h-auto rounded-3xl backdrop-blur-sm backdrop-brightness-200 shadow-sm shadow-black/20">
              <div className="mx-auto p-3 justify-center mb-4 w-fit relative right-[0px] text-lg shadow-sm flex p-1 lg:rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200">
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
                {!parsubData && !error && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex justify-center items-center"
                  >
                    <div className="spinner"></div>
                  </motion.div>
                )}
                {parsubData && parsubData.subset && selectedTab === "subset" && (
                  <motion.div
                    key="sub-table"
                    initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.5 }}
                  >
                    <DataTable
                      data={formatSubsetData(parsubData.subset)}
                      showDelete={false}
                      maxHeight={300}
                      maxW={130}
                    />
                  </motion.div>
                )}
                {parsubData && parsubData.part && selectedTab === "part" && (
                  <motion.div
                    key="part-table"
                    initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.5 }}
                  >
                    <DataTable
                      data={formatSubsetData(parsubData.part, "part")}
                      showDelete={false}
                      maxHeight={300}
                      maxW={150}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </AnimatePresence>
        <div className="sets text-lg shadow-sm flex flex-wrap lg:flex-nowrap gap-12 p-5 lg:rounded-4xl shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 w-full"></div>
      </div>
    </motion.div>
  );
}