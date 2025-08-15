import { Link } from 'react-router-dom'
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { FileText, Users } from 'lucide-react'
import { useLanguage } from '@/shared/hooks/use-language'
import type { Language } from '@/shared/lib/i18n/types'

type TermsSection = {
  title: string
  content?: string | string[]
  subsections?: Array<{ title: string; content: string[] }>
}

type TermsDoc = {
  title: string
  lastUpdate: string
  backToRegister: string
  sections: TermsSection[]
}

const TERMS_DOC: Record<Language, TermsDoc> = {
  en: {
    title: 'Terms of Service',
    lastUpdate: 'Last updated: 15.08.2025',
    backToRegister: 'Back to Registration',
    sections: [
      {
        title: '1. General Provisions',
        content: [
          'Welcome to Smart Study - an intelligent platform for assessing and developing student skills with an AI-powered recommendation system.',
          'By using our services, you agree to comply with these terms of service. If you disagree with any terms, please do not use our platform.',
        ],
      },
      {
        title: '2. Service Description',
        content: [
          'Smart Study provides the following services:',
          'Online courses and educational materials',
          'Testing and knowledge assessment system',
          'Personalized AI-based recommendations',
          'Event calendar and deadlines',
          'Tools for teachers and students',
          'Learning progress analytics',
        ],
      },
      {
        title: '3. User Rights and Responsibilities',
        subsections: [
          {
            title: '3.1 User Rights:',
            content: [
              'Access to all platform features according to your role',
              'Receiving quality educational content',
              'Technical support and assistance',
              'Personal data protection',
            ],
          },
          {
            title: '3.2 User Responsibilities:',
            content: [
              'Provide accurate information during registration',
              'Maintain academic integrity',
              'Do not violate copyright',
              'Respect other platform users',
              'Do not use the platform for illegal activities',
            ],
          },
        ],
      },
      {
        title: '4. Intellectual Property',
        content: [
          'All materials on the Smart Study platform, including courses, tests, videos, texts, and software, are protected by copyright and are the property of Smart Study or our partners.',
          'Users are granted a limited license to use materials exclusively for personal learning. Copying, distribution, or commercial use is prohibited without written consent.',
        ],
      },
      {
        title: '5. Academic Integrity',
        content: [
          'Smart Study supports academic integrity principles. Prohibited:',
          'Cheating during tests and exams',
          'Plagiarism in assignments',
          'Providing answers to other students',
          'Using third-party programs to bypass the system',
          'Creating fake accounts',
          'Violation of academic integrity may result in account suspension.',
        ],
      },
      {
        title: '6. Payment and Refunds',
        content: [
          'Smart Study provides free access to basic platform features. Premium features may be available for an additional fee.',
          'All payments are final. Refunds are only possible in exceptional cases according to our refund policy.',
        ],
      },
      {
        title: '7. Limitation of Liability',
        content: [
          'Smart Study makes every effort to ensure stable platform operation but does not guarantee uninterrupted access to services.',
          'We are not responsible for:',
          'Technical failures beyond our control',
          'Data loss due to user actions',
          'Indirect damages from platform use',
        ],
      },
      {
        title: '8. Service Termination',
        content: [
          'Smart Study reserves the right to suspend or terminate services for users who violate these terms of service.',
          'Users can stop using the platform at any time by deleting their account.',
        ],
      },
      {
        title: '9. Changes to Terms of Service',
        content: [
          'Smart Study may update these terms of service. We will notify users of significant changes through the platform or email.',
          'Continuing to use the platform after changes means your agreement with the new terms.',
        ],
      },
      {
        title: '10. Contact Information',
        content: [
          'If you have questions about these terms of service, contact us:',
          'Email: support@smartstudy.ua',
          'Phone: +380 (44) 123-45-67',
          'Address: Kyiv, Khreshchatyk St., 1',
        ],
      },
    ],
  },
  uk: {
    title: 'Умови використання',
    lastUpdate: 'Останнє оновлення: 15.08.2025',
    backToRegister: 'Повернутися до реєстрації',
    sections: [
      {
        title: '1. Загальні положення',
        content: [
          'Вітаємо вас на платформі Smart Study - інтелектуальній платформі для оцінки та розвитку навичок студентів з системою рекомендацій на основі штучного інтелекту.',
          'Використовуючи наші послуги, ви погоджуєтесь дотримуватися цих умов використання. Якщо ви не згодні з будь-якими умовами, будь ласка, не використовуйте нашу платформу.',
        ],
      },
      {
        title: '2. Опис послуг',
        content: [
          'Smart Study надає такі послуги:',
          'Онлайн-курси та навчальні матеріали',
          'Система тестування та оцінювання знань',
          'Персоналізовані рекомендації на основі ШІ',
          'Календар подій та дедлайнів',
          'Інструменти для викладачів та студентів',
          'Аналітика прогресу навчання',
        ],
      },
      {
        title: "3. Права та обов'язки користувачів",
        subsections: [
          {
            title: '3.1 Права користувачів:',
            content: [
              'Доступ до всіх функцій платформи відповідно до вашої ролі',
              'Отримання якісного навчального контенту',
              'Технічна підтримка та допомога',
              'Захист персональних даних',
            ],
          },
          {
            title: "3.2 Обов'язки користувачів:",
            content: [
              'Надавати достовірну інформацію при реєстрації',
              'Дотримуватись академічної доброчесності',
              'Не порушувати авторські права',
              'Поважати інших користувачів платформи',
              'Не використовувати платформу для незаконних дій',
            ],
          },
        ],
      },
      {
        title: '4. Інтелектуальна власність',
        content: [
          'Всі матеріали на платформі Smart Study, включаючи курси, тести, відео, тексти та програмне забезпечення, захищені авторським правом і є власністю Smart Study або наших партнерів.',
          'Користувачам надається обмежена ліцензія на використання матеріалів виключно для особистого навчання. Заборонено копіювання, розповсюдження або комерційне використання без письмової згоди.',
        ],
      },
      {
        title: '5. Академічна доброчесність',
        content: [
          'Smart Study підтримує принципи академічної доброчесності. Заборонено:',
          'Списування під час тестів та екзаменів',
          'Плагіат у виконанні завдань',
          'Надання відповідей іншим студентам',
          'Використання сторонніх програм для обходу системи',
          'Створення фальшивих акаунтів',
          'Порушення академічної доброчесності може призвести до блокування акаунта.',
        ],
      },
      {
        title: '6. Оплата та відшкодування',
        content: [
          'Smart Study надає безкоштовний доступ до базових функцій платформи. Преміум-функції можуть бути доступні за додаткову плату.',
          'Всі платежі є остаточними. Відшкодування можливе лише у виняткових випадках відповідно до нашої політики повернення коштів.',
        ],
      },
      {
        title: '7. Обмеження відповідальності',
        content: [
          'Smart Study докладає максимальних зусиль для забезпечення стабільної роботи платформи, але не гарантує безперервного доступу до послуг.',
          'Ми не несемо відповідальності за:',
          'Технічні збої поза нашим контролем',
          'Втрату даних через дії користувачів',
          'Непрямі збитки від використання платформи',
        ],
      },
      {
        title: '8. Припинення послуг',
        content: [
          'Smart Study залишає за собою право призупинити або припинити надання послуг користувачам, які порушують ці умови використання.',
          'Користувачі можуть у будь-який час припинити використання платформи, видаливши свій акаунт.',
        ],
      },
      {
        title: '9. Зміни в умовах використання',
        content: [
          'Smart Study може оновлювати ці умови використання. Про суттєві зміни ми повідомимо користувачів через платформу або електронну пошту.',
          'Продовження використання платформи після внесення змін означає вашу згоду з новими умовами.',
        ],
      },
      {
        title: '10. Контактна інформація',
        content: [
          "Якщо у вас є питання щодо цих умов використання, зв'яжіться з нами:",
          'Email: support@smartstudy.ua',
          'Phone: +380 (44) 123-45-67',
          'Address: м. Київ, вул. Хрещатик, 1',
        ],
      },
    ],
  },
}

export const TermsOfServiceContent = () => {
  const [language] = useLanguage()
  const doc = TERMS_DOC[language]

  const renderContent = (content?: string | string[]) => {
    if (!content) return null
    if (typeof content === 'string') return <p>{content}</p>
    return content.map((item, index) => {
      if (
        item.includes(':') &&
        !item.startsWith('Email:') &&
        !item.startsWith('Phone:') &&
        !item.startsWith('Address:')
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
          <FileText className="w-8 h-8 text-brand-600 dark:text-brand-400" />
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
                  <Users className="w-5 h-5 text-brand-600 dark:text-brand-400" />
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
