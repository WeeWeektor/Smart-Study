import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AlertTriangle, Loader2, ShieldCheck, XCircle } from 'lucide-react'
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

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-4">
      <div className="mb-8 font-bold text-2xl text-brand-700">
        {t('SmartStudy Verification')}
      </div>

      <Card
        className={`w-full max-w-md shadow-xl border-t-4 ${isValid ? 'border-t-green-500' : 'border-t-red-500'}`}
      >
        <CardHeader className="text-center pb-2">
          <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-slate-100">
            {isValid ? (
              <ShieldCheck className="h-12 w-12 text-green-600" />
            ) : isRevoked ? (
              <AlertTriangle className="h-12 w-12 text-orange-500" />
            ) : (
              <XCircle className="h-12 w-12 text-red-500" />
            )}
          </div>
          <CardTitle className="text-xl">
            {isValid
              ? t('Сертифікат Дійсний')
              : isRevoked
                ? t('Сертифікат Анульовано')
                : t('Сертифікат не знайдено')}
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-6 text-center">
          {data && !error ? (
            <div className="space-y-4 animate-in fade-in zoom-in duration-300">
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-1">
                  {t('Видано студенту')}
                </p>
                <p className="font-bold text-lg text-slate-800">
                  {data.student_name}
                </p>
              </div>

              <div className="space-y-1">
                <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold">
                  {t('За успішне завершення курсу')}
                </p>
                <h3 className="font-semibold text-brand-700 text-xl leading-tight py-2">
                  {data.course_title}
                </h3>
              </div>

              <div className="flex justify-between text-sm text-slate-500 border-t pt-4 px-4">
                <div className="text-left">
                  <span className="block text-xs text-slate-400">
                    {t('Дата видачі')}
                  </span>
                  <span className="font-medium text-slate-700">
                    {data.issued_at}
                  </span>
                </div>
                <div className="text-right">
                  <span className="block text-xs text-slate-400">
                    {t('ID Сертифікату')}
                  </span>
                  <span className="font-mono font-medium text-slate-700">
                    {data.certificate_id}
                  </span>
                </div>
              </div>

              {!data.is_valid && (
                <div className="bg-red-50 text-red-700 px-4 py-2 rounded text-sm mt-4">
                  {t('Увага: Цей сертифікат було відкликано адміністрацією.')}
                </div>
              )}
            </div>
          ) : (
            <div className="text-slate-600 py-4">
              <p>
                {t(
                  'Ми не знайшли запису про цей сертифікат у нашій базі даних.'
                )}
              </p>
              <p className="mt-2 text-sm text-slate-400">
                {t('ID')}: {id}
              </p>
            </div>
          )}

          <div className="pt-6 mt-6">
            <Link to="/">
              <Button variant="outline" className="w-full">
                {t('Перейти на головну')}
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default VerifyPage
