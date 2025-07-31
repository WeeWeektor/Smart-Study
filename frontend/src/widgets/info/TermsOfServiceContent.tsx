import { Link } from 'react-router-dom'
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { FileText, Users } from 'lucide-react'

export const TermsOfServiceContent = () => {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-brand-600" />
        </div>
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Умови використання
        </h1>
        <p className="text-lg text-slate-600">
          Останнє оновлення: {new Date().toLocaleDateString('uk-UA')}
        </p>
      </div>

      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="w-5 h-5 text-brand-600" />
              <span>1. Загальні положення</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Вітаємо вас на платформі Smart Study - інтелектуальній платформі
              для оцінки та розвитку навичок студентів з системою рекомендацій
              на основі штучного інтелекту.
            </p>
            <p>
              Використовуючи наші послуги, ви погоджуєтесь дотримуватися цих
              умов використання. Якщо ви не згодні з будь-якими умовами, будь
              ласка, не використовуйте нашу платформу.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>2. Опис послуг</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>Smart Study надає такі послуги:</p>
            <ul>
              <li>Онлайн-курси та навчальні матеріали</li>
              <li>Система тестування та оцінювання знань</li>
              <li>Персоналізовані рекомендації на основі ШІ</li>
              <li>Календар подій та дедлайнів</li>
              <li>Інструменти для викладачів та студентів</li>
              <li>Аналітика прогресу навчання</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>3. Права та обов'язки користувачів</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <h4>3.1 Права користувачів:</h4>
            <ul>
              <li>Доступ до всіх функцій платформи відповідно до вашої ролі</li>
              <li>Отримання якісного навчального контенту</li>
              <li>Технічна підтримка та допомога</li>
              <li>Захист персональних даних</li>
            </ul>

            <h4>3.2 Обов'язки користувачів:</h4>
            <ul>
              <li>Надавати достовірну інформацію при реєстрації</li>
              <li>Дотримуватись академічної доброчесності</li>
              <li>Не порушувати авторські права</li>
              <li>Поважати інших користувачів платформи</li>
              <li>Не використовувати платформу для незаконних дій</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>4. Інтелектуальна власність</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Всі матеріали на платформі Smart Study, включаючи курси, тести,
              відео, тексти та програмне забезпечення, захищені авторським
              правом і є власністю Smart Study або наших партнерів.
            </p>
            <p>
              Користувачам надається обмежена ліцензія на використання
              матеріалів виключно для особистого навчання. Заборонено
              копіювання, розповсюдження або комерційне використання без
              письмової згоди.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>5. Академічна доброчесність</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Smart Study підтримує принципи академічної доброчесності.
              Заборонено:
            </p>
            <ul>
              <li>Списування під час тестів та екзаменів</li>
              <li>Плагіат у виконанні завдань</li>
              <li>Надання відповідей іншим студентам</li>
              <li>Використання сторонніх програм для обходу системи</li>
              <li>Створення фальшивих акаунтів</li>
            </ul>
            <p>
              Порушення академічної доброчесності може призвести до блокування
              акаунта.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>6. Оплата та відшкодування</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Smart Study надає безкоштовний доступ до базових функцій
              платформи. Преміум-функції можуть бути доступні за додаткову
              плату.
            </p>
            <p>
              Всі платежі є остаточними. Відшкодування можливе лише у виняткових
              випадках відповідно до нашої політики повернення коштів.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>7. Обмеження відповідальності</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Smart Study докладає максимальних зусиль для забезпечення
              стабільної роботи платформи, але не гарантує безперервного доступу
              до послуг.
            </p>
            <p>Ми не несемо відповідальності за:</p>
            <ul>
              <li>Технічні збої поза нашим контролем</li>
              <li>Втрату даних через дії користувачів</li>
              <li>Непрямі збитки від використання платформи</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>8. Припинення послуг</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Smart Study залишає за собою право призупинити або припинити
              надання послуг користувачам, які порушують ці умови використання.
            </p>
            <p>
              Користувачі можуть у будь-який час припинити використання
              платформи, видаливши свій акаунт.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>9. Зміни в умовах використання</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Smart Study може оновлювати ці умови використання. Про суттєві
              зміни ми повідомимо користувачів через платформу або електронну
              пошту.
            </p>
            <p>
              Продовження використання платформи після внесення змін означає
              вашу згоду з новими умовами.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>10. Контактна інформація</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-slate max-w-none">
            <p>
              Якщо у вас є питання щодо цих умов використання, зв'яжіться з
              нами:
            </p>
            <ul>
              <li>
                <strong>Email:</strong> support@smartstudy.ua
              </li>
              <li>
                <strong>Телефон:</strong> +380 (44) 123-45-67
              </li>
              <li>
                <strong>Адреса:</strong> м. Київ, вул. Хрещатик, 1
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      <div className="mt-12 text-center">
        <Link to="/register">
          <Button className="bg-brand-600 hover:bg-brand-700">
            Повернутися до реєстрації
          </Button>
        </Link>
      </div>
    </div>
  )
}
