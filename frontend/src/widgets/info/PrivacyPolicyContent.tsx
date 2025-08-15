import { Link } from 'react-router-dom'
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Shield, Lock, Eye, Database } from 'lucide-react'
import { useLanguage } from '@/shared/hooks/use-language'
import type { Language } from '@/shared/lib/i18n/types'

type PrivacySection = {
  title: string
  content?: string | string[]
  subsections?: Array<{ title: string; content: string[] }>
}

type PrivacyDoc = {
  title: string
  lastUpdate: string
  sections: PrivacySection[]
  backToRegister: string
}

const PRIVACY_DOC: Record<Language, PrivacyDoc> = {
  en: {
    title: 'Privacy Policy',
    lastUpdate: 'Last updated: 15.08.2025',
    backToRegister: 'Back to Registration',
    sections: [
      {
        title: '1. General Information',
        content: [
          'Smart Study ("we", "our company") respects your privacy and is committed to protecting your personal data. This privacy policy explains how we collect, use, and protect your information.',
          'By using our platform, you agree to the practices described in this privacy policy.',
        ],
      },
      {
        title: '2. Information We Collect',
        subsections: [
          {
            title: '2.1 Personal Information:',
            content: [
              'First and last name',
              'Email address',
              'Phone number (optional)',
              'Role (student/teacher)',
              'Profile photo (optional)',
            ],
          },
          {
            title: '2.2 Educational Information:',
            content: [
              'Test results and grades',
              'Course progress',
              'Time spent on the platform',
              'Assignment responses',
              'Comments and discussions',
            ],
          },
          {
            title: '2.3 Technical Information:',
            content: [
              'IP address',
              'Browser type and operating system',
              'Visit time and activity',
              'Cookies and similar technologies',
            ],
          },
        ],
      },
      {
        title: '3. How We Use Your Information',
        content: [
          'We use the collected information for:',
          'Service provision: providing access to courses, tests, and educational materials',
          'Personalization: creating individual recommendations based on AI',
          'Assessment: tracking progress and providing feedback',
          'Communication: sending important messages and updates',
          'Platform improvement: analyzing usage to optimize features',
          'Security: preventing fraud and protecting the platform',
        ],
      },
      {
        title: '4. Artificial Intelligence and Analytics',
        content: [
          'Smart Study uses artificial intelligence technologies for:',
          'Analyzing learning patterns and behavior',
          'Creating personalized course recommendations',
          'Automatically grading assignments',
          'Identifying learning difficulties',
          'Optimizing the learning process',
          'All AI algorithms work with anonymized data and do not violate your privacy.',
        ],
      },
      {
        title: '5. Disclosure of Information to Third Parties',
        content: [
          'We do not sell, exchange, or transfer your personal data to third parties, except:',
          'Service providers: companies that help operate the platform (hosting, analytics)',
          'Legal requirements: when necessary according to law',
          'Security: to protect user rights and safety',
          'User consent: when you explicitly give permission',
        ],
      },
      {
        title: '6. Data Protection',
        content: [
          'We use modern security measures:',
          'Encryption: SSL/TLS for data transmission',
          'Secure storage: encrypted databases',
          'Access control: limited access to personal data',
          'Regular audits: security system checks',
          'Backup: protection against data loss',
        ],
      },
      {
        title: '7. Your Rights',
        content: [
          'According to personal data protection legislation, you have the right to:',
          'Access: obtain a copy of your personal data',
          'Correction: make changes to inaccurate information',
          'Deletion: delete your account and data',
          'Portability: obtain data in a structured format',
          'Objection: refuse data processing',
          'Restriction: limit the use of your data',
        ],
      },
      {
        title: '8. Cookies and Similar Technologies',
        content: [
          'We use cookies to improve your experience:',
          'Essential cookies: for basic functionality',
          'Functional cookies: for remembering settings',
          'Analytics cookies: for understanding platform usage',
          'You can manage cookies through browser settings, but this may affect platform functionality.',
        ],
      },
      {
        title: '9. Data Retention',
        content: [
          'We store your personal data as long as necessary for:',
          'Providing our services',
          'Fulfilling legal obligations',
          'Resolving disputes',
          'Ensuring security',
          'After account deletion, your personal data will be deleted within 30 days, except for data we are required to retain by law.',
        ],
      },
      {
        title: '10. Children and Minors',
        content: [
          'Our platform is intended for users aged 13 and older. If you are under 18, we recommend obtaining parental or guardian consent before using the platform.',
          'We do not knowingly collect personal data from children under 13 without parental consent.',
        ],
      },
      {
        title: '11. Changes to Privacy Policy',
        content: [
          'Smart Study may update this privacy policy. We will notify you of significant changes through:',
          'Platform notifications',
          'Email',
          'Updating the date on this page',
        ],
      },
      {
        title: '12. Privacy Contact Information',
        content: [
          'If you have questions about this privacy policy or the processing of your personal data, contact us:',
          'Email: privacy@smartstudy.ua',
          'Phone: +380 (44) 123-45-67',
          'Postal address: Kyiv, Khreshchatyk St., 1, office 101',
          'We will respond to your request within 30 business days.',
        ],
      },
    ],
  },
  uk: {
    title: 'Політика конфіденційності',
    lastUpdate: 'Останнє оновлення: 15.08.2025',
    backToRegister: 'Повернутися до реєстрації',
    sections: [
      {
        title: '1. Загальна інформація',
        content: [
          'Smart Study ("ми", "наша компанія") поважає вашу конфіденційність і зобов\'язується захищати ваші персональні дані. Ця політика конфіденційності пояснює, як ми збираємо, використовуємо та захищаємо вашу інформацію.',
          'Використовуючи нашу платформу, ви погоджуєтесь з практиками, описаними в цій політиці конфіденційності.',
        ],
      },
      {
        title: '2. Інформація, яку ми збираємо',
        subsections: [
          {
            title: '2.1 Особиста інформація:',
            content: [
              "Ім'я та прізвище",
              'Адреса електронної пошти',
              'Номер телефону (опціонально)',
              'Роль (студент/викладач)',
              'Фотографія профілю (опціонально)',
            ],
          },
          {
            title: '2.2 Навчальна інформація:',
            content: [
              'Результати тестів та оцінки',
              'Прогрес у курсах',
              'Час, проведений на платформі',
              'Відповіді на завдання',
              'Коментарі та обговорення',
            ],
          },
          {
            title: '2.3 Технічна інформація:',
            content: [
              'IP-адреса',
              'Тип браузера та операційна система',
              'Час відвідування та активності',
              'Cookies та подібні технології',
            ],
          },
        ],
      },
      {
        title: '3. Як ми використовуємо вашу інформацію',
        content: [
          'Ми використовуємо зібрану інформацію для:',
          'Надання послуг: забезпечення доступу до курсів, тестів та навчальних матеріалів',
          'Персоналізація: створення індивідуальних рекомендацій на основі ШІ',
          "Оцінювання: відстеження прогресу та надання зворотного зв'язку",
          'Комунікація: надсилання важливих повідомлень та оновлень',
          'Покращення платформи: аналіз використання для оптимізації функцій',
          'Безпека: запобігання шахрайству та захист платформи',
        ],
      },
      {
        title: '4. Штучний інтелект та аналітика',
        content: [
          'Smart Study використовує технології штучного інтелекту для:',
          'Аналізу навчальних патернів та поведінки',
          'Створення персоналізованих рекомендацій курсів',
          'Автоматичного оцінювання завдань',
          'Виявлення складностей у навчанні',
          'Оптимізації навчального процесу',
          'Всі алгоритми ШІ працюють з анонімізованими даними та не порушують вашу конфіденційність.',
        ],
      },
      {
        title: '5. Розкриття інформації третім сторонам',
        content: [
          'Ми не продаємо, не обмінюємо та не передаємо ваші персональні дані третім сторонам, за винятком:',
          'Надавачі послуг: компанії, які допомагають в роботі платформи (хостинг, аналітика)',
          'Правові вимоги: коли це необхідно згідно з законом',
          'Безпека: для захисту прав та безпеки користувачів',
          'Згода користувача: коли ви явно даєте дозвіл',
        ],
      },
      {
        title: '6. Захист даних',
        content: [
          'Ми використовуємо сучасні засоби захисту:',
          'Шифрування: SSL/TLS для передачі даних',
          'Безпечне зберігання: зашифровані бази даних',
          'Контроль доступу: обмежений доступ до персональних даних',
          'Регулярні аудити: перевірка систем безпеки',
          'Резервне копіювання: захист від втрати даних',
        ],
      },
      {
        title: '7. Ваші права',
        content: [
          'Відповідно до законодавства про захист персональних даних, ви маєте право:',
          'Доступ: отримати копію ваших персональних даних',
          'Виправлення: внести зміни до неточної інформації',
          'Видалення: видалити ваш акаунт та дані',
          'Портабельність: отримати дані в структурованому форматі',
          'Заперечення: відмовитися від обробки даних',
          'Обмеження: обмежити використання ваших даних',
        ],
      },
      {
        title: '8. Cookies та подібні технології',
        content: [
          'Ми використовуємо cookies для покращення вашого досвіду:',
          'Необхідні cookies: для роботи базового функціоналу',
          "Функціональні cookies: для запам'ятовування налаштувань",
          'Аналітичні cookies: для розуміння використання платформи',
          'Ви можете керувати cookies через налаштування браузера, але це може вплинути на функціональність платформи.',
        ],
      },
      {
        title: '9. Зберігання даних',
        content: [
          'Ми зберігаємо ваші персональні дані стільки, скільки це необхідно для:',
          'Надання наших послуг',
          "Виконання юридичних зобов'язань",
          'Вирішення спорів',
          'Забезпечення безпеки',
          "Після видалення акаунта ваші персональні дані будуть видалені протягом 30 днів, за винятком даних, які ми зобов'язані зберігати згідно з законом.",
        ],
      },
      {
        title: '10. Діти та неповнолітні',
        content: [
          'Наша платформа призначена для користувачів віком від 13 років. Якщо ви молодше 18 років, рекомендуємо отримати згоду батьків або опікунів перед використанням платформи.',
          'Ми не свідомо не збираємо персональні дані дітей віком до 13 років без згоди батьків.',
        ],
      },
      {
        title: '11. Зміни в політиці конфіденційності',
        content: [
          'Smart Study може оновлювати цю політику конфіденційності. Про суттєві зміни ми повідомимо вас через:',
          'Повідомлення на платформі',
          'Електронну пошту',
          'Оновлення дати на цій сторінці',
        ],
      },
      {
        title: '12. Контакти з питань конфіденційності',
        content: [
          "Якщо у вас є питання щодо цієї політики конфіденційності або обробки ваших персональних даних, зв'яжіться з нами:",
          'Email: privacy@smartstudy.ua',
          'Телефон: +380 (44) 123-45-67',
          'Поштова адреса: м. Київ, вул. Хрещатик, 1, офіс 101',
          'Ми відповімо на ваш запит протягом 30 робочих днів.',
        ],
      },
    ],
  },
}

export const PrivacyPolicyContent = () => {
  const [language] = useLanguage()
  const doc = PRIVACY_DOC[language]

  const renderContent = (content?: string | string[]) => {
    if (!content) return null
    if (typeof content === 'string') {
      return <p>{content}</p>
    }
    return content.map((item, index) => {
      if (
        item.includes(':') &&
        !item.startsWith('Email:') &&
        !item.startsWith('Phone:') &&
        !item.startsWith('Postal address:')
      ) {
        const [title, ...rest] = item.split(':')
        return (
          <div key={index}>
            <h4>{title}:</h4>
            {rest.length > 0 && <p>{rest.join(':')}</p>}
          </div>
        )
      }
      return <p key={index}>{item}</p>
    })
  }

  return (
    <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <div className="w-16 h-16 bg-brand-100 dark:bg-brand-900 rounded-full flex items-center justify-center mx-auto mb-4">
          <Shield className="w-8 h-8 text-brand-600 dark:text-brand-400" />
        </div>
        <h1 className="text-4xl font-bold text-foreground mb-4">{doc.title}</h1>
        <p className="text-lg text-muted-foreground">
          {doc.lastUpdate}
          {new Date().toLocaleDateString(language === 'uk' ? 'uk-UA' : 'en-US')}
        </p>
      </div>

      <div className="space-y-8">
        {doc.sections.map((section, index) => (
          <Card key={section.title}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {index === 0 && (
                  <Eye className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                )}
                {index === 1 && (
                  <Database className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                )}
                {index === 5 && (
                  <Lock className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                )}
                <span>{section.title}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="prose max-w-none text-foreground">
              {renderContent(section.content)}
              {section.subsections?.map((subsection, subIndex) => (
                <div key={subIndex} className="mb-4">
                  <h4>{subsection.title}</h4>
                  <ul>
                    {subsection.content.map((item, itemIndex) => (
                      <li key={itemIndex}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-12 text-center">
        <Link to="/register">
          <Button className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white">
            {doc.backToRegister}
          </Button>
        </Link>
      </div>
    </div>
  )
}
