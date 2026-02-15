import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowLeft,
  Loader2,
  ShieldCheck,
  XCircle,
} from 'lucide-react'
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import {
  type CertificateData,
  userCourseCertificateService,
} from '@/features/course'
import { useI18n } from '@/shared/lib'

const VerifyPage = () => {
  const { t } = useI18n()
  const { id } = useParams<{ id: string }>()

  const [data, setData] = useState<CertificateData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!id) return

    setLoading(true)
    userCourseCertificateService
      .verifyCertificate(id)
      .then(res => {
        setData(res)
        setError(false)
      })
      .catch(() => {
        setError(true)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-10 h-10 animate-spin text-brand-600" />
      </div>
    )
  }

  const isValid = !error && data?.is_valid
  const isRevoked = !error && data && !data.is_valid

  const statusStyles = isValid
    ? {
        borderColor: 'border-t-green-500',
        iconBg: 'bg-green-100',
        iconColor: 'text-green-600',
        icon: <ShieldCheck className="h-10 w-10 text-green-600" />,
        titleColor: 'text-green-700',
      }
    : isRevoked
      ? {
          borderColor: 'border-t-orange-500',
          iconBg: 'bg-orange-100',
          iconColor: 'text-orange-600',
          icon: <AlertTriangle className="h-10 w-10 text-orange-600" />,
          titleColor: 'text-orange-700',
        }
      : {
          borderColor: 'border-t-red-500',
          iconBg: 'bg-red-100',
          iconColor: 'text-red-600',
          icon: <XCircle className="h-10 w-10 text-red-600" />,
          titleColor: 'text-red-700',
        }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-slate-50 to-slate-100 p-4">
      <div className="mb-8 font-bold text-3xl text-brand-700 tracking-tight">
        {t('SmartStudy Verification')}
      </div>

      <Card
        className={`w-full max-w-md shadow-2xl bg-white dark:bg-slate-900 border-t-8 ${statusStyles.borderColor}`}
      >
        <CardHeader className="text-center pb-2 pt-8">
          <div
            className={`mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full ${statusStyles.iconBg}`}
          >
            {statusStyles.icon}
          </div>
          <CardTitle
            className={`text-2xl font-bold ${statusStyles.titleColor}`}
          >
            {isValid
              ? t('Сертифікат Дійсний')
              : isRevoked
                ? t('Сертифікат Анульовано')
                : t('Сертифікат не знайдено')}
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-8 text-center px-8 pb-10">
          {data && !error ? (
            <div className="space-y-6 animate-in fade-in zoom-in duration-300">
              <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-100 dark:border-slate-700">
                <p className="text-xs uppercase tracking-widest text-slate-500 font-semibold mb-2">
                  {t('Видано студенту')}
                </p>
                <p className="font-bold text-xl text-slate-900 dark:text-slate-100">
                  {data.student_name}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
                  {t('За успішне завершення курсу')}
                </p>
                <h3 className="text-lg font-bold text-brand-600 leading-snug px-4">
                  {data.course_title}
                </h3>
              </div>

              <div className="flex justify-between items-center text-sm text-slate-500 border-t border-slate-100 dark:border-slate-800 pt-6 mt-4">
                <div className="text-left">
                  <span className="block text-xs text-slate-400 mb-1">
                    {t('Дата видачі')}
                  </span>
                  <span className="font-semibold text-slate-700 dark:text-slate-300">
                    {data.issued_at}
                  </span>
                </div>
                <div className="text-right">
                  <span className="block text-xs text-slate-400 mb-1">
                    {t('ID Сертифікату')}
                  </span>
                  <span className="font-mono font-medium text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs">
                    {data.certificate_id}
                  </span>
                </div>
              </div>

              {!data.is_valid && (
                <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm font-medium border border-red-100">
                  {t('Увага: Цей сертифікат було відкликано адміністрацією.')}
                </div>
              )}
            </div>
          ) : (
            <div className="text-slate-600 py-8">
              <p className="text-lg mb-2">
                {t(
                  'Ми не знайшли запису про цей сертифікат у нашій базі даних.'
                )}
              </p>
              <p className="text-sm text-slate-400 bg-slate-100 inline-block px-3 py-1 rounded-full">
                {t('ID')}: {id}
              </p>
            </div>
          )}

          <div className="pt-4">
            <Link to="/">
              <Button
                variant="outline"
                className="w-full gap-2 hover:bg-slate-50 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                {t('Перейти на головну')}
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      <div className="mt-8 text-slate-400 text-sm">
        &copy; {new Date().getFullYear()} SmartStudy Platform
      </div>
    </div>
  )
}

export default VerifyPage
