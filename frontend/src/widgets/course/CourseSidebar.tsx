import { useEffect, useState } from 'react'
import {
  CheckSquare,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  FileText,
  Folder,
  Lock,
  PlayCircle,
} from 'lucide-react'
import { useI18n } from '@/shared/lib'
import type { CourseStructureResponse, NormalizedItem } from '@/features/course'
import { normalizeCourseStructure } from '@/shared/lib/course/normalizeStructure.ts'

interface CourseSidebarProps {
  isCollapsible?: boolean
  onCollapseChange?: (isCollapsed: boolean) => void
  data: CourseStructureResponse | null

  isEnrolled?: boolean
  onItemClick?: (id: string, type: string) => void
  activeItemId?: string | null
}

export const CourseSidebar = ({
  isCollapsible = false,
  onCollapseChange,
  data,
  isEnrolled = false,
  onItemClick,
  activeItemId,
}: CourseSidebarProps) => {
  const { t } = useI18n()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const [structure, setStructure] = useState<NormalizedItem[]>([])

  useEffect(() => {
    if (data) {
      const normalized = normalizeCourseStructure(data)
      setStructure(normalized)
    }
  }, [data])

  useEffect(() => {
    if (activeItemId && structure.length > 0) {
      setStructure(prev =>
        prev.map(item => {
          const hasActiveChild = item.children?.some(
            child => child.id === activeItemId
          )
          if (hasActiveChild && !item.isOpen) {
            return { ...item, isOpen: true }
          }
          return item
        })
      )
    }
  }, [activeItemId])

  const toggleSidebar = () => {
    if (!isCollapsible) return
    const newState = !isCollapsed
    setIsCollapsed(newState)
    if (onCollapseChange) {
      onCollapseChange(newState)
    }
  }

  const toggleModule = (moduleId: string) => {
    if (isCollapsed) return
    setStructure(prev =>
      prev.map(item =>
        item.id === moduleId ? { ...item, isOpen: !item.isOpen } : item
      )
    )
  }

  const handleContentClick = (item: NormalizedItem) => {
    if (isCollapsed) return

    if (!isEnrolled) return

    if (onItemClick) {
      onItemClick(item.id, item.type)
    }
  }

  const getIcon = (type: string, isActive: boolean) => {
    switch (type) {
      case 'lesson':
        return (
          <PlayCircle
            className={`w-4 h-4 ${isActive ? 'text-brand-600 dark:text-brand-400' : 'text-slate-500'}`}
          />
        )
      case 'module-test':
      case 'course-test':
        return (
          <CheckSquare
            className={`w-4 h-4 ${isActive ? 'text-brand-600 dark:text-brand-400' : 'text-green-600'}`}
          />
        )
      case 'module':
        return <Folder className="w-4 h-4 text-blue-600" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const getItemClasses = (itemId: string) => {
    const isActive = activeItemId === itemId

    let classes =
      'flex items-center justify-between group p-2 rounded-md text-sm transition-colors border border-transparent '

    if (isActive) {
      classes +=
        'bg-brand-50 dark:bg-brand-900/40 text-brand-600 dark:text-brand-400 font-medium cursor-default'
    } else if (isEnrolled) {
      classes +=
        'cursor-pointer hover:bg-muted hover:border-border text-foreground/80'
    } else {
      classes += 'cursor-default opacity-60 text-muted-foreground'
    }

    return classes
  }

  //   return (
  //     <aside
  //       className={`fixed inset-y-0 right-0 z-40 bg-sidebar border-l border-sidebar-border transition-all duration-300 ease-in-out flex flex-col ${
  //         isCollapsed ? 'w-20' : 'w-80'
  //       }`}
  //     >
  //       <div
  //         className={`h-16 flex items-center px-4 border-b border-sidebar-border shrink-0 ${isCollapsed ? 'justify-center' : 'justify-between'}`}
  //       >
  //         {isCollapsible && (
  //           <button
  //             onClick={toggleSidebar}
  //             className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground transition-colors"
  //           >
  //             {isCollapsed ? (
  //               <ChevronLeft className="w-5 h-5" />
  //             ) : (
  //               <ChevronRight className="w-5 h-5" />
  //             )}
  //           </button>
  //         )}
  //
  //         <h2
  //           className={`font-semibold text-foreground whitespace-nowrap overflow-hidden transition-all duration-300 ${
  //             isCollapsed ? 'w-0 opacity-0 hidden' : 'ml-3 flex-1 opacity-100'
  //           }`}
  //         >
  //           {t('Зміст курсу')}
  //         </h2>
  //       </div>
  //
  //       <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-700">
  //         {!isCollapsed ? (
  //           structure.map(item => (
  //             <div key={item.id} className="select-none">
  //               {item.type === 'module' ? (
  //                 <div className="space-y-1">
  //                   <button
  //                     onClick={() => toggleModule(item.id)}
  //                     className="w-full flex items-center justify-between p-2 rounded-md hover:bg-muted/50 transition-colors text-left cursor-pointer"
  //                   >
  //                     <div className="flex items-center gap-2 overflow-hidden">
  //                       <span className="text-xs font-bold text-muted-foreground uppercase whitespace-nowrap">
  //                         {t('Модуль')} {item.order}
  //                       </span>
  //                       <span
  //                         className="text-sm font-medium truncate"
  //                         title={item.title}
  //                       >
  //                         {item.title}
  //                       </span>
  //                     </div>
  //                     <ChevronDown
  //                       className={`w-4 h-4 text-muted-foreground transition-transform duration-200 ${item.isOpen ? 'rotate-180' : ''}`}
  //                     />
  //                   </button>
  //
  //                   {item.isOpen && item.children && (
  //                     <div className="pl-2 space-y-1 animate-in slide-in-from-top-2 duration-200">
  //                       {item.children.map(child => (
  //                         <div
  //                           key={child.id}
  //                           onClick={() => handleContentClick(child)}
  //                           className={getItemClasses(child.id)}
  //                         >
  //                           <div className="flex items-center gap-3 overflow-hidden">
  //                             {getIcon(child.type)}
  //                             <span
  //                               className="truncate text-foreground/90"
  //                               title={child.title}
  //                             >
  //                               {child.title}
  //                             </span>
  //                           </div>
  //                           <div className="flex items-center gap-2">
  //                             {child.meta && (
  //                               <span className="text-xs text-muted-foreground whitespace-nowrap opacity-70 group-hover:opacity-100">
  //                                 {child.meta}
  //                               </span>
  //                             )}
  //                             {!isEnrolled && (
  //                               <Lock className="w-3 h-3 text-muted-foreground opacity-50" />
  //                             )}
  //                           </div>
  //                         </div>
  //                       ))}
  //                       {item.children.length === 0 && (
  //                         <div className="pl-9 text-xs text-muted-foreground italic py-1">
  //                           {t('Модуль порожній')}
  //                         </div>
  //                       )}
  //                     </div>
  //                   )}
  //                 </div>
  //               ) : (
  //                 <div
  //                   onClick={() => handleContentClick(item)}
  //                   className={`mt-2 ${getItemClasses(item.id)}`}
  //                 >
  //                   <div className="flex items-center gap-3 overflow-hidden">
  //                     {getIcon(item.type)}
  //                     <span
  //                       className="truncate font-medium text-foreground"
  //                       title={item.title}
  //                     >
  //                       {item.title}
  //                     </span>
  //                   </div>
  //                   <div className="flex items-center gap-2">
  //                     {item.meta && (
  //                       <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
  //                         {item.meta}
  //                       </span>
  //                     )}
  //                     {!isEnrolled && (
  //                       <Lock className="w-3 h-3 text-muted-foreground opacity-50" />
  //                     )}
  //                   </div>
  //                 </div>
  //               )}
  //             </div>
  //           ))
  //         ) : (
  //           <div className="flex flex-col items-center gap-4 mt-2">
  //             {structure.map(item => (
  //               <div
  //                 key={item.id}
  //                 className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shadow-sm border transition-colors cursor-pointer
  //                   ${
  //                     item.type === 'module'
  //                       ? 'bg-muted text-foreground hover:bg-primary hover:text-primary-foreground border-border'
  //                       : 'bg-green-100 text-green-700 hover:bg-green-600 hover:text-white border-green-200 dark:bg-green-900/30 dark:text-green-400'
  //                   }`}
  //                 title={item.title}
  //               >
  //                 {item.order}
  //               </div>
  //             ))}
  //           </div>
  //         )}
  //       </div>
  //     </aside>
  //   )
  // }

  return (
    <aside
      className={`fixed inset-y-0 right-0 z-40 bg-sidebar border-l border-sidebar-border transition-all duration-300 ease-in-out flex flex-col ${
        isCollapsed ? 'w-20' : 'w-80'
      }`}
    >
      <div
        className={`h-16 flex items-center px-4 border-b border-sidebar-border shrink-0 ${isCollapsed ? 'justify-center' : 'justify-between'}`}
      >
        {isCollapsible && (
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground transition-colors"
          >
            {isCollapsed ? (
              <ChevronLeft className="w-5 h-5" />
            ) : (
              <ChevronRight className="w-5 h-5" />
            )}
          </button>
        )}

        <h2
          className={`font-semibold text-foreground whitespace-nowrap overflow-hidden transition-all duration-300 ${
            isCollapsed ? 'w-0 opacity-0 hidden' : 'ml-3 flex-1 opacity-100'
          }`}
        >
          {t('Зміст курсу')}
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-700">
        {!isCollapsed ? (
          structure.map(item => (
            <div key={item.id} className="select-none">
              {item.type === 'module' ? (
                <div className="space-y-1">
                  <button
                    onClick={() => toggleModule(item.id)}
                    className="w-full flex items-center justify-between p-2 rounded-md hover:bg-muted/50 transition-colors text-left cursor-pointer"
                  >
                    <div className="flex items-center gap-2 overflow-hidden">
                      <span className="text-xs font-bold text-muted-foreground uppercase whitespace-nowrap">
                        {t('Модуль')} {item.order}
                      </span>
                      <span
                        className="text-sm font-medium truncate"
                        title={item.title}
                      >
                        {item.title}
                      </span>
                    </div>
                    <ChevronDown
                      className={`w-4 h-4 text-muted-foreground transition-transform duration-200 ${item.isOpen ? 'rotate-180' : ''}`}
                    />
                  </button>

                  {item.isOpen && item.children && (
                    <div className="pl-2 space-y-1 animate-in slide-in-from-top-2 duration-200">
                      {item.children.map(child => (
                        <div
                          key={child.id}
                          onClick={() => handleContentClick(child)}
                          className={getItemClasses(child.id)}
                        >
                          <div className="flex items-center gap-3 overflow-hidden">
                            {getIcon(child.type, activeItemId === child.id)}
                            <span className="truncate" title={child.title}>
                              {child.title}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {child.meta && (
                              <span className="text-xs text-muted-foreground whitespace-nowrap opacity-70">
                                {child.meta}
                              </span>
                            )}
                            {!isEnrolled && (
                              <Lock className="w-3 h-3 text-muted-foreground opacity-50" />
                            )}
                          </div>
                        </div>
                      ))}
                      {item.children.length === 0 && (
                        <div className="pl-9 text-xs text-muted-foreground italic py-1">
                          {t('Модуль порожній')}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div
                  onClick={() => handleContentClick(item)}
                  className={`${getItemClasses(item.id)} mt-2`}
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    {getIcon(item.type, activeItemId === item.id)}
                    <span className="truncate" title={item.title}>
                      {item.title}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.meta && (
                      <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                        {item.meta}
                      </span>
                    )}
                    {!isEnrolled && (
                      <Lock className="w-3 h-3 text-muted-foreground opacity-50" />
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center gap-4 mt-2">
            {structure.map(item => (
              <div
                key={item.id}
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shadow-sm border transition-colors cursor-pointer
                  ${
                    item.type === 'module'
                      ? 'bg-muted text-foreground hover:bg-primary hover:text-primary-foreground border-border'
                      : 'bg-green-100 text-green-700 hover:bg-green-600 hover:text-white border-green-200 dark:bg-green-900/30 dark:text-green-400'
                  }`}
                title={item.title}
              >
                {item.order}
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}

export default CourseSidebar
