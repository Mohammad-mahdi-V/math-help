import classNames from "classnames";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import DataTable from "./table";
import * as math from 'mathjs';

export default function SetsForm() {
  const [sets, setSets] = useState([]); 
  const [currentSet, setCurrentSet] = useState({ name: '', value: '', index: null }); 
  const [numSets, setNumSets] = useState(1);
  const [showAi, setShowAi] = useState(false);
  const [aiInput, setAiInput] = useState('');
  const [aiOutput, setAiOutput] = useState('پاسخی دریافت نشده است');
  const [selectedSet, setSelectedSet] = useState({ name: "", value: "", index: null });
  const [nameError, setNameError] = useState("");
  const [membError, setMembError] = useState("");
  const [editMode, setEditMode] = useState(false);
  const [isFirstLoad, setIsFirstLoad] = useState(true);

  useEffect(() => {
    const timeout = setTimeout(() => setIsFirstLoad(false), 50);
    return () => clearTimeout(timeout);
  }, []);

  function addSet() {
    const newSet = {
      name: currentSet.name.toUpperCase(),
      value: currentSet.value,
    };
    if (editMode && selectedSet.index !== null) {
      setSets(sets.map((set, index) => (index === selectedSet.index ? newSet : set)));
      setEditMode(false);
    } else {
      setSets([...sets, newSet]);
      setNumSets(numSets + 1);
    }
    setCurrentSet({ name: "", value: "", index: null });
  }

  function handleDelete(index) {
    setSets(sets.filter((_, i) => i !== index));
    setNumSets(numSets - 1);
    if (selectedSet.index === index) {
      if (selectedSet.name === currentSet.name) {
        setCurrentSet({ name: "", value: "", index: null });
        setEditMode(false);
      }
      setSelectedSet({ name: "", value: "", index: null });
    }
  }

  function handleSelect(set, index) {
    if (set === null && index === null) {
      setSelectedSet({ name: "", value: "", index: null });
    } else {
      if (editMode && index !== currentSet.index) {
        setEditMode(false);
        setCurrentSet({ name: "", value: "", index: null });
      }
      setSelectedSet({ name: set["نام مجموعه"], value: set["اعضای مجموعه"], index });
      setNameError("");
      setMembError("");
    }
  }

  function aiRequset() {
    console.log("SSSS");
  }

  function nameErrorCheck(v) {
    if (sets.some((s) => s.name.toUpperCase() === v.toUpperCase())) {
      setNameError("این نام قبلاً استفاده شده");
    } else {
      setNameError(""); 
    }
  }


  function validateNestedSet(setString) {
    const trimmedValue = setString.trim();

    if (!trimmedValue.startsWith("{") || !trimmedValue.endsWith("}")) {
      return "عبارت باید با اکلاد شروع و با اکلاد به پایان برسد";
    }

    let braceCount = 0;
    for (let i = 0; i < trimmedValue.length; i++) {
      if (trimmedValue[i] === "{") braceCount++;
      if (trimmedValue[i] === "}") braceCount--;
      if (braceCount < 0) return "تعداد اکلاد باز با بسته برابر نیست";
    }
    if (braceCount !== 0) return "تعداد اکلاد باز با بسته برابر نیست";

    if (trimmedValue.slice(1, -1).trim() === "") {
      return "مجموعه تهی پشتیبانی نمی‌شود";
    }

    function parseSetContent(content) {
      let current = "";
      let braceLevel = 0;
      let elements = [];
      let lastWasComma = false;

      for (let i = 0; i < content.length; i++) {
        const char = content[i];

        if (char === "{") {
          braceLevel++;
          current += char;
        } else if (char === "}") {
          braceLevel--;
          current += char;
          if (braceLevel === 0 && current) {
            elements.push(current);
            current = "";
            lastWasComma = false;
          }
        } else if (char === "," && braceLevel === 0) {
          if (lastWasComma) {
            return "چندین کاما متوالی مجاز نیست";
          }
          if (current.trim()) {
            elements.push(current.trim());
            current = "";
            lastWasComma = true;
          } 
        } else {
          current += char;
          lastWasComma = false;
        }
      }
      if (current.trim()) {
        elements.push(current.trim());
      }

      if (lastWasComma) {
        return "کاما در انتهای مجموعه مجاز نیست";
      }

      const elementSet = new Set();
      for (let element of elements) {
        if (elementSet.has(element)) {
          return "عناصر تکراری در مجموعه مجاز نیست";
        }
        elementSet.add(element);
      }

      const validElementPattern = /^[a-zA-Z0-9!@#$%^&*()_+><?|/.]+$/;
      for (let element of elements) {
        if (element.startsWith("{") && element.endsWith("}")) {
          const subSetError = parseSetContent(element.slice(1, -1));
          if (subSetError) return subSetError;
        } else {
          if (!validElementPattern.test(element)) {
            return "عنصر مجموعه نامعتبر است";
          }
          try {
            const node = math.parse(`[${element}]`);
            if (!node.isArrayNode) {
              return "عنصر مجموعه نامعتبر است";
            }
          } catch (error) {
            if (!validElementPattern.test(element)) {
              return "عنصر مجموعه نامعتبر است";
            }
          }
        }
      }
      return null;
    }

    const content = trimmedValue.slice(1, -1);
    const error = parseSetContent(content);
    return error ? error : "";
  }

  function membErrorCheck(v) {
    const trimmedValue = v.trim();

    if (trimmedValue === "") {
      setMembError("");
      setCurrentSet({ name: currentSet.name, value: "", index: null });
    } else {
      const error = validateNestedSet(trimmedValue);
      setMembError(error);
    }
  }
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
      className="relative mx-auto lg:max-w-[1024px] lg:top-30 top-50 shadow-sm shadow-black/20 backdrop-blur-sm backdrop-brightness-200"
    >
      <div className="sets text-lg shadow-sm flex flex-wrap lg:flex-nowrap gap-12 p-5 lg:rounded-4xl roud shadow-black/20 bg-blue-950/20 backdrop-blur-sm backdrop-brightness-200 w-full ">
        <div className="sets-form min-h-[326px] order-2 lg:order-1 w-full mx-auto max-w-[768px] lg:max-w-auto lg:w-7/12 h-full ">
          <form
            onSubmit={(e) => { e.preventDefault(); addSet(); }}
            className="p-4 min-h-[189px] rounded-3xl backdrop-blur-sm backdrop-brightness-200 shadow-sm shadow-black/20"
          >
            <AnimatePresence mode="wait">
              {(numSets <= 6 || editMode) && (
                <motion.div
                  initial={isFirstLoad ? false : { borderRadius: 32, opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ borderRadius: 32, opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="set-name-form mt-5 gap-4 flex flex-wrap ">
                    <div className="input gap-4 w-full flex items-center">
                      <span className="w-1/2 text-white text-shadow-sm text-shadow-black/40 ">
                        نام مجموعه {currentSet.index !== null ? currentSet.index + 1 : numSets} :
                      </span>
                      <input
                        type="text"
                        maxLength={1}
                        value={currentSet.name.toUpperCase()}
                        placeholder={`نام مجموعه ${currentSet.index !== null ? currentSet.index + 1 : numSets}`}
                        onChange={(e) => {
                          const value = e.target.value;
                          if (/^[a-zA-Z]*$/.test(value)) {
                            setCurrentSet({ ...currentSet, name: value, index: null });
                            nameErrorCheck(value);
                          } else {
                            setNameError("از یک حرف انگلیسی فقط می‌توان استفاده نمود");
                          }
                        }}
                        className={classNames(
                          "text-lg transform text-white duration-500 w-full p-2 shadow-sm shadow-black/30 rounded-lg focus-visible:shadow focus-visible:shadow-lg focus-visible:shadow-black/40 focus-visible:scale-102 focus-visible:outline-0",
                          { "shadow-red-700 focus-visible:shadow-red-700": nameError }
                        )}
                      />
                    </div>
                    <span
                      className={classNames(
                        "input-error text-red-700 text-shadow-sm text-shadow-black/20 overflow-auto w-full transition collapse opacity-0 duration-500",
                        { "visible mb-4 opacity-100": nameError }
                      )}
                    >
                      {nameError}
                    </span>
                  </div>
                  <div className="set-memb-form gap-4 flex flex-wrap ">
                    <div className="input gap-4 w-full flex items-center">
                      <span className="w-1/2 text-white text-shadow-sm text-shadow-black/40 ">
                        اعضای مجموعه {currentSet.index !== null ? currentSet.index + 1 : numSets} :
                      </span>
                      <input
                        type="text"
                        value={currentSet.value}
                        placeholder={`اعضای مجموعه ${currentSet.index !== null ? currentSet.index + 1 : numSets}`}
                        onChange={(e) => {
                          const newValue = e.target.value;
                          setCurrentSet({ ...currentSet, value: newValue, index: null });
                          membErrorCheck(newValue);
                        }}
                        className={classNames(
                          "text-lg math-input transform w-full duration-500 text-white p-2 shadow-sm shadow-black/30 rounded-lg focus-visible:shadow focus-visible:shadow-lg focus-visible:shadow-black/40 focus-visible:scale-102 focus-visible:outline-0",
                          { "shadow-red-700 focus-visible:shadow-red-700": membError }
                        )}
                      />
                    </div>
                    <span
                      className={classNames(
                        "input-error text-red-700 text-shadow-sm text-shadow-black/20 overflow-auto w-full transition collapse opacity-0 duration-500",
                        { "visible mb-4 opacity-100": membError }
                      )}
                    >
                      {membError}
                    </span>
                  </div>
                  <div className="flex gap-4">
                    <AnimatePresence mode="wait">
                      {!editMode && (
                        <motion.button
                          key="editOff"
                          initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.9 }}
                          type="submit"
                          className="w-full transform duration-500 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 rounded-lg disabled:blur-[1.5px] disabled:hover:shadow disabled:hover:scale-100 disabled:hover:bg-blue-950/30"
                          disabled={!currentSet.name || !currentSet.value || membError || nameError}
                        >
                          ثبت مجموعه
                        </motion.button>
                      )}
                      {editMode && (
                        <motion.button
                          key="editOn"
                          initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.9 }}
                          type="submit"
                          className="w-full transform duration-500 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 rounded-lg disabled:blur-[1.5px] disabled:hover:shadow disabled:hover:scale-100 disabled:hover:bg-blue-950/30"
                          disabled={!currentSet.name || !currentSet.value || membError || nameError}
                        >
                          ویرایش مجموعه
                        </motion.button>
                      )}
                    </AnimatePresence>
                    <AnimatePresence mode="wait">
                      {!showAi && (
                        <motion.button
                          key="aiOff"
                          initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.9 }}
                          type="button"
                          className="w-full transform duration-500 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 flex items-center justify-center rounded-lg"
                          onClick={() => setShowAi(!showAi)}
                        >
                          <i className="fa-solid animate-bounce fa-sparkles text-xl"></i>
                        </motion.button>
                      )}
                      {showAi && (
                        <motion.button
                          key="aiOn"
                          initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.9 }}
                          type="button"
                          className="w-full transform duration-500 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 flex items-center justify-center rounded-lg"
                          onClick={() => setShowAi(!showAi)}
                        >
                          <i className="fa-light fa-xmark-large text-xl"></i>
                        </motion.button>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              )}
              {(numSets > 6 && !editMode) && (
                <motion.div
                  key="setFormEnd"
                  initial={{ borderRadius: 32, opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ borderRadius: 32, opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.5 }}
                  className="absolute text-center text-white start-5 end-5 top-1/2 -translate-y-1/2"
                >
                  <span>نمی‌توان بیش از ۶ مجموعه ثبت کرد. پردازش مجموعه‌ها یا ویرایش را کلیک کنید</span>
                </motion.div>
              )}
            </AnimatePresence>
          </form>

          <div className="set-final-btn w-full mt-4 p-4 rounded-3xl backdrop-blur-sm backdrop-brightness-200 shadow-sm shadow-black/20">
            <button
              type="button"
              className="w-full transform duration-500 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 disabled:blur-[1.5px] disabled:hover:shadow disabled:hover:scale-100 disabled:hover:bg-blue-950/30 p-2.5 rounded-lg"
              disabled={sets.length === 0}
            >
              پردازش مجموعه‌ها
            </button>
            <AnimatePresence mode="wait">
              {!editMode && (
                <motion.button
                  key="edit"
                  initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.5 }}
                  type="button"
                  className="w-full transform duration-500 mt-3 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 disabled:blur-[1.5px] disabled:hover:shadow disabled:hover:scale-100 disabled:hover:bg-blue-950/30 rounded-lg"
                  disabled={selectedSet.name === ""}
                  onClick={() => {
                    setCurrentSet({ ...selectedSet });
                    setEditMode(true);
                    console.log(currentSet);
                  }}
                >
                  ویرایش مجموعه انتخاب شده
                </motion.button>
              )}
              {editMode && (
                <motion.button
                  key="cancel"
                  initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.5 }}
                  type="button"
                  className="w-full transform duration-500 mt-3 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 disabled:blur-[1.5px] disabled:hover:shadow disabled:hover:scale-100 disabled:hover:bg-blue-950/30 rounded-lg"
                  onClick={() => {
                    setCurrentSet({ name: "", value: "", index: null });
                    setEditMode(false);
                  }}
                >
                  لغو ویرایش
                </motion.button>
              )}
            </AnimatePresence>
          </div>
        </div>
        <AnimatePresence mode="wait">
          {!showAi && (
            <motion.div
              key="sets-table"
              initial={isFirstLoad ? false : { borderRadius: 32, opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ borderRadius: 32, opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.5 }}
              className="sets-table w-full mx-auto p-2 lg:order-2 h-100 lg:h-auto max-w-[768px] lg:w-7/12 lg:min-w-7/12 rounded-3xl backdrop-blur-sm backdrop-brightness-200 shadow-sm shadow-black/20"
            >
              <AnimatePresence mode="wait">
                {sets.length === 0 ? (
                  <motion.div
                    key="empty"
                    initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.5 }}
                    className="w-full h-full text-white text-shadow-sm text-shadow-black/30 flex items-center justify-center text-center"
                  >
                    <span>هیچ مجموعه‌ای وارد نشده است</span>
                  </motion.div>
                ) : (
                  <motion.div
                    key="table"
                    initial={isFirstLoad ? false : { opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.5 }}
                  >
                    <DataTable
                      data={sets.map(item => ({"نام مجموعه": item.name, "اعضای مجموعه": item.value}))}
                      showDelete={true}
                      onDelete={handleDelete}
                      onSelect={handleSelect}
                      maxHeight={326}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {showAi && (
            <motion.div
              key="sets-ai"
              initial={{ borderRadius: 32, opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ borderRadius: 32, opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.5 }}
              className="sets-ai w-full min-h-[326px] lg:order-2 mx-auto max-w-[768px] lg:w-7/12 lg:min-w-7/12 rounded-3xl backdrop-blur-sm backdrop-brightness-200 shadow-sm shadow-black/20"
            >
              <form
                onSubmit={(e) => { e.preventDefault(); aiRequset(); }}
                className="p-5 content-between h-full flex flex-wrap w-full"
              >
                <div className="ai-input-form gap-4 w-full flex flex-wrap ">
                  <span className="text-white text-shadow-sm h-1/12 content-start text-shadow-black/40">
                    مجموعه خود را توصیف کنید :
                  </span>
                  <textarea
                    type="text"
                    rows={5}
                    value={aiInput}
                    placeholder="مجموعه خود را توصیف کنید :"
                    onChange={(e) => setAiInput(e.target.value)}
                    className="text-lg text-white transform duration-500 w-full p-2 shadow-sm shadow-black/30 rounded-2xl focus-visible:shadow focus-visible:shadow-lg focus-visible:shadow-black/40 focus-visible:scale-102 focus-visible:outline-0"
                  />
                </div>
                <p className="w-full mt-4 text-xl text-center overflow-auto">{aiOutput}</p>
                <div className="ai-sets-btn w-full flex-end max-h-[42px] flex mt-4 gap-4 mx-4 ">
                  <button
                    type="submit"
                    className="w-full transform duration-500 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 rounded-lg"
                  >
                    ارسال
                  </button>
                  <button
                    type="button"
                    className="w-full transform duration-500 shadow bg-blue-950/30 hover:shadow-lg hover:scale-102 text-white hover:bg-blue-950/50 shadow-black/40 p-2.5 rounded-lg disabled:hover:bg-blue-950/30 disabled:hover:shadow disabled:hover:scale-100 disabled:blur-[1.5px]"
                    disabled={aiOutput === 'پاسخی دریافت نشده است' || aiRequset === 'درحال دریافت جواب'}
                    onClick={() => setCurrentSet({ name: currentSet.name, value: aiOutput })}
                  >
                    تایید پاسخ
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}