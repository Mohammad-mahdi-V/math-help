import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
} from '@tanstack/react-table'
import { motion ,AnimatePresence } from "framer-motion";
import { useMemo, useState,useEffect} from 'react'

export default function DataTable({ data, showDelete = true, onDelete, onSelect,maxHeight }) {
  const [selectedRowIndex, setSelectedRowIndex] = useState(null)
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const columns = useMemo(() => {
  const keys = Object.keys(data[0] || {})
  const tableCols = keys.map((key) => ({
      accessorKey: key,
      header: key,
      cell: ({ getValue }) => (
        <span className="block max-w-[200px] overflow-auto text-nowrap   text-gray-100">
          {getValue()?.toString()}
        </span>
      ),
    }))

    const actionCol = {
      header: 'عملیات',
      id: 'actions',
      cell: ({ row }) => (
        <div className="flex gap-3   justify-center">
          {showDelete && (
            <button
              onClick={() => {
                onDelete?.(row.index)
                if (selectedRowIndex === row.index) {
                  setSelectedRowIndex(null)
                  onSelect?.(null, null) 
                }
              }}
              className="group relative  flex items-center justify-center px-3 py-1.5 backdrop-blur-lg shadow-sm shadow-black/40 hover:shadow-black/50 text-white rounded-lg transition-all duration-500 shadow-sm hover:shadow-lg hover:scale-105"
              title="حذف ایتم"
            >
                
              <i className="fa-light fa-trash "></i>
            </button>
          )}
        </div>
      ),
    }

    return [...tableCols, actionCol]
  }, [data, showDelete, onDelete, selectedRowIndex])

  const table = useReactTable({
    data,
    columns,
    
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })
  useEffect(() => {
      const timeout = setTimeout(() => setIsFirstLoad(false), 50); // بعد از 50 میلی‌ثانیه حالت بارگذاری اولیه رو خاموش کن
      return () => clearTimeout(timeout);
    }, []);
  return (
    <div className={`w-full overflow-auto  max-h-[${maxHeight}px]  p-4`}>
      <table className="w-full  text-white text-right border-separate border-spacing-y-3">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className=" mx-4 backdrop-blur-xl  shadow-sm shadow-black/40 rounded-lg">
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                  className="cursor-pointer  text-center   p-3 font-semibold text-gray-100 select-none transition-all duration-500 hover:shadow-lg shdaow-black  hover:bg-blue-950/20 rounded-lg"
                >
                  <div className="flex items-center text-nowrap  justify-center  gap-2">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    <span className="text-gray-400">
                      {header.column.getIsSorted() === 'asc' && (
                        <i className="fa-light fa-arrow-up text-black "></i>
                      )}
                      {header.column.getIsSorted() === 'desc' && (
                        <i className="fa-light fa-arrow-down  text-black"></i>
                      )}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          <AnimatePresence>
          {table.getRowModel().rows.map((row) => (
            <motion.tr
              initial={isFirstLoad? false:{  opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{  opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.5 }}
              key={row.id}
              onClick={() => {
                if (selectedRowIndex === row.index) {
                  setSelectedRowIndex(null)
                  onSelect?.(null, null)
                } else {
                  setSelectedRowIndex(row.index)
                  onSelect?.(row.original, row.index)
                }
              }}
              className={`group text-center backdrop-blur-lg shadow-sm shadow-black/40  rounded-xl transition-all duration-300 cursor-pointer ${
                selectedRowIndex === row.index
                  ? ' shadow-md  scale-95'
                  : '  hover:shadow-lg'
              }`}
            > 
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="p-3 felx  rounded-none ">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </motion.tr>
            
          ))}
          </AnimatePresence>
        </tbody>
      </table>
    </div>
  )
}