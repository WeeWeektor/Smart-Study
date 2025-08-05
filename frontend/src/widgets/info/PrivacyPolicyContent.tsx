import { Link } from 'react-router-dom'
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Shield, Lock, Eye, Database } from 'lucide-react'

export const PrivacyPolicyContent = () => {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <div className="w-16 h-16 bg-brand-100 dark:bg-brand-900 rounded-full flex items-center justify-center mx-auto mb-4">
          <Shield className="w-8 h-8 text-brand-600 dark:text-brand-400" />
        </div>
        <h1 className="text-4xl font-bold text-foreground mb-4">
          Політика конфіденційності
        </h1>
        <p className="text-lg text-muted-foreground">
          Останнє оновлення: {new Date().toLocaleDateString('uk-UA')}
        </p>
      </div>

      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              <span>1. Загальна інформація</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>
              Smart Study ("ми", "наша компанія") поважає вашу конфіденційність
              і зобов'язується захищати ваші персональні дані. Ця політика
              конфіденційності пояснює, як ми збираємо, використовуємо та
              захищаємо вашу інформацію.
            </p>
            <p>
              Використовуючи нашу платформу, ви погоджуєтесь з практиками,
              описаними в цій політиці конфіденційності.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              <span>2. Інформація, яку ми збираємо</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <h4>2.1 Особиста інформація:</h4>
            <ul>
              <li>Ім'я та прізвище</li>
              <li>Адреса електронної пошти</li>
              <li>Номер телефону (опціонально)</li>
              <li>Роль (студент/викладач)</li>
              <li>Фотографія профілю (опціонально)</li>
            </ul>

            <h4>2.2 Навчальна інформація:</h4>
            <ul>
              <li>Результати тестів та оцінки</li>
              <li>Прогрес у курсах</li>
              <li>Час, проведений на платформі</li>
              <li>Відповіді на завдання</li>
              <li>Коментарі та обговорення</li>
            </ul>

            <h4>2.3 Технічна інформація:</h4>
            <ul>
              <li>IP-адреса</li>
              <li>Тип браузера та операційна система</li>
              <li>Час відвідування та активності</li>
              <li>Cookies та подібні технології</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>3. Як ми використовуємо вашу інформацію</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>Ми використовуємо зібрану інформацію для:</p>
            <ul>
              <li>
                <strong>Надання послуг:</strong> забезпечення доступу до курсів,
                тестів та навчальних матеріалів
              </li>
              <li>
                <strong>Персоналізація:</strong> створення індивідуальних
                рекомендацій на основі ШІ
              </li>
              <li>
                <strong>Оцінювання:</strong> відстеження прогресу та надання
                зворотного зв'язку
              </li>
              <li>
                <strong>Комунікація:</strong> надсилання важливих повідомлень та
                оновлень
              </li>
              <li>
                <strong>Покращення платформи:</strong> аналіз використання для
                оптимізації функцій
              </li>
              <li>
                <strong>Безпека:</strong> запобігання шахрайству та захист
                платформи
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>4. Штучний інтелект та аналітика</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>Smart Study використовує технології штучного інтелекту для:</p>
            <ul>
              <li>Аналізу навчальних патернів та поведінки</li>
              <li>Створення персоналізованих рекомендацій курсів</li>
              <li>Автоматичного оцінювання завдань</li>
              <li>Виявлення складностей у навчанні</li>
              <li>Оптимізації навчального процесу</li>
            </ul>
            <p>
              Всі алгоритми ШІ працюють з анонімізованими даними та не порушують
              вашу конфіденційність.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>5. Розкриття інформації третім сторонам</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>
              Ми не продаємо, не обмінюємо та не передаємо ваші персональні дані
              третім сторонам, за винятком:
            </p>
            <ul>
              <li>
                <strong>Надавачі послуг:</strong> компанії, які допомагають в
                роботі платформи (хостинг, аналітика)
              </li>
              <li>
                <strong>Правові вимоги:</strong> коли це необхідно згідно з
                законом
              </li>
              <li>
                <strong>Безпека:</strong> для захисту прав та безпеки
                користувачів
              </li>
              <li>
                <strong>Згода користувача:</strong> коли ви явно даєте дозвіл
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Lock className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              <span>6. Захист даних</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>Ми використовуємо сучасні засоби захисту:</p>
            <ul>
              <li>
                <strong>Шифрування:</strong> SSL/TLS для передачі даних
              </li>
              <li>
                <strong>Безпечне зберігання:</strong> зашифровані бази даних
              </li>
              <li>
                <strong>Контроль доступу:</strong> обмежений доступ до
                персональних даних
              </li>
              <li>
                <strong>Регулярні аудити:</strong> перевірка систем безпеки
              </li>
              <li>
                <strong>Резервне копіювання:</strong> захист від втрати даних
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>7. Ваші права</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>
              Відповідно до законодавства про захист персональних даних, ви
              маєте право:
            </p>
            <ul>
              <li>
                <strong>Доступ:</strong> отримати копію ваших персональних даних
              </li>
              <li>
                <strong>Виправлення:</strong> внести зміни до неточної
                інформації
              </li>
              <li>
                <strong>Видалення:</strong> видалити ваш акаунт та дані
              </li>
              <li>
                <strong>Портабельність:</strong> отримати дані в структурованому
                форматі
              </li>
              <li>
                <strong>Заперечення:</strong> відмовитися від обробки даних
              </li>
              <li>
                <strong>Обмеження:</strong> обмежити використання ваших даних
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>8. Cookies та подібні технології</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>Ми використовуємо cookies для покращення вашого досвіду:</p>
            <ul>
              <li>
                <strong>Необхідні cookies:</strong> для роботи базового
                функціоналу
              </li>
              <li>
                <strong>Функціональні cookies:</strong> для запам'ятовування
                налаштувань
              </li>
              <li>
                <strong>Аналітичні cookies:</strong> для розуміння використання
                платформи
              </li>
            </ul>
            <p>
              Ви можете керувати cookies через налаштування браузера, але це
              може вплинути на функціональність платформи.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>9. Зберігання даних</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>
              Ми зберігаємо ваші персональні дані стільки, скільки це необхідно
              для:
            </p>
            <ul>
              <li>Надання наших послуг</li>
              <li>Виконання юридичних зобов'язань</li>
              <li>Вирішення спорів</li>
              <li>Забезпечення безпеки</li>
            </ul>
            <p>
              Після видалення акаунта ваші персональні дані будуть видалені
              протягом 30 днів, за винятком даних, які ми зобов'язані зберігати
              згідно з законом.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>10. Діти та неповнолітні</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>
              Наша платформа призначена для користувачів віком від 13 років.
              Якщо ви молодше 18 років, рекомендуємо отримати згоду батьків або
              опікунів перед використанням платформи.
            </p>
            <p>
              Ми не свідомо не збираємо персональні дані дітей віком до 13 років
              без згоди батьків.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>11. Зміни в політиці конфіденційності</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>
              Smart Study може оновлювати цю політику конфіденційності. Про
              суттєві зміни ми повідомимо вас через:
            </p>
            <ul>
              <li>Повідомлення на платформі</li>
              <li>Електронну пошту</li>
              <li>Оновлення дати на цій сторінці</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>12. Контакти з питань конфіденційності</CardTitle>
          </CardHeader>
          <CardContent className="prose max-w-none text-foreground">
            <p>
              Якщо у вас є питання щодо цієї політики конфіденційності або
              обробки ваших персональних даних, зв'яжіться з нами:
            </p>
            <ul>
              <li>
                <strong>Email:</strong> privacy@smartstudy.ua
              </li>
              <li>
                <strong>Телефон:</strong> +380 (44) 123-45-67
              </li>
              <li>
                <strong>Поштова адреса:</strong> м. Київ, вул. Хрещатик, 1, офіс
                101
              </li>
            </ul>
            <p>Ми відповімо на ваш запит протягом 30 робочих днів.</p>
          </CardContent>
        </Card>
      </div>

      <div className="mt-12 text-center">
        <Link to="/register">
          <Button className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white">
            Повернутися до реєстрації
          </Button>
        </Link>
      </div>
    </div>
  )
}
