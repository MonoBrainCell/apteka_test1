# apteka_test1
 Тестовое задание по сбору данных с сайта
 имя парсера: __Apteka_scraper__
<ol>
<li>Пример выполненного парсинга по заданию находится в файле data.json. В него были собраны данные из следующих категорий товаров: Ватные диски,Термометры,Ингаляторы</li>
<li>Прокси были добавлены (scrapy rotating proxies), но из-за медленной работы парсера (использовались только общедоступные проски-адреса) было решено отключить данный функционал (settings.py)</li>
<li>Парсер, как и было указано в задании осуществляет сбор данных о товарах по нескольким категориям; но был реализован подход ручного определения целевых категорий из имеющихся на сайте: При запуске парсера в консоли отображается предложение указать целевые категории товаров. Указанные категории проверяются на наличие в списке доступных и в случае их наличия формируются url-ы соответствующих категорий</li>
<li>Особенности сбора словаря:
 <ol>
  <li>"stock"->"count" - при исследовании веб-ресурса не обнаружено возможности определить точное количество товара оставшееся на складе</li>
  <li>"assets"->"view360" и "assets"->"video" - при исследовании веб-ресурса не обнаружено данных типов информации о товарах</li>
  <li>"metadata"->"__ description" - описания товара представляли из себя контент различной длины и содержания, поэтому было принятно решение забирать весь html-код, который вложен непосредственно в контейнер элемента, отвечающего за описание товара</li>
  <li>"metadata"->"СТРАНА ПРОИЗВОДИТЕЛЬ" - единственная характеристика товара, которая наблюдалась в карточках товаров, а также не была зафиксирована в других частях словаря</li>
  <li>"variants" - при исследовании веб-ресура не было найдено разделения товаров на варианты</li>
 </ol>
</li>
<li>Описание методов класса парсера:
 <ol>
  <li>parse - метод запуска процесса парсинга. В рамках метода осуществляется определение целевых категорий товаров (при помощи ввода данных через консоль) и запуск обхода выбранных категорий</li>
  <li>parse_single_cat - метод осуществляет обход списка карточек товаров отдельной категории</li>
  <li>parse_goods_card - метод осуществляет парсинг отдельной карточки товара</li>
  <li>form_price_data - метод используется для формирование части данных, относящихся к цене товара</li>
  <li>form_assets_data - метод используется для формирование части данных, относящихся к визуальной презентации товара</li>
  <li>form_metadata_data - метод используется для формирование части данных, относящихся к текстовому описанию товара</li>
  <li>get_cats_list - метод используется для получения списка всех существующих категорий товаров на сайте</li>
  <li>parse_cats - метод используется для выделения из текстового контента тега <script> информации о категориях товаров и их преобразования в словарь</li>
  <li>form_cats_plane_dict - рекурсивный метод используется для формирования одноуровневого(плоского) словаря с категориями ([адрес_категории]="название категории"); данный словарь используется при выборе категорий товаров и формировании соответствующих им url-ов</li>
  </ol>
 </li>
 </ol>
