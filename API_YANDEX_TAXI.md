# API Яндекс.Такси для партнеров сервиса


Общие сведения: https://fleet.taxi.yandex.ru/docs/api/concepts/index.html
Ресурсы API https://fleet.taxi.yandex.ru/docs/api/reference/index.html

Cars
Получение автомобиля	GET /v2/parks/vehicles/car
Получение списка автомобилей	POST /v1/parks/cars/list

ContractorProfiles
Получение профиля водителя (курьера)	GET /v2/parks/contractors/driver-profile
Получение списка профилей водителей (курьеров)	POST /v1/parks/driver-profiles/list

DriverWorkRules
Получение списка условий работы	GET /v1/parks/driver-work-rules

Orders
Получение списка заказов	POST /v1/parks/orders/list
Получение трека по заказу	POST /v1/parks/orders/track

Transactions
Получение списка категорий транзакций	POST /v2/parks/transactions/categories/list
Получение списка транзакций по водителю (курьеру)	POST /v2/parks/driver-profiles/transactions/list
Получение списка транзакций по заказам	POST /v2/parks/orders/transactions/list
Получение списка транзакций по парку	POST /v2/parks/transactions/list
