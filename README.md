# Скрипт для постинга паков пикч с дёрпибуры или твайбуры на табуне

## Для чего нужен

Для автоматического составления таких паков, как пак [Дёрпи](https://tabun.everypony.ru/blog/I_love_Derpy/197952.html), [Селестии](https://tabun.everypony.ru/blog/Order_of_Celestia/197945.html), [Луны](https://tabun.everypony.ru/blog/Order_of_Luna/197980.html), [Найтмер Мун](https://tabun.everypony.ru/blog/vyxefcetrg787cowg/197829.html), [Твайки](https://tabun.everypony.ru/blog/Twilight/197978.html), [Старлайт](https://tabun.everypony.ru/blog/equalitychurch/197920.html), ну и, конечно, [Лиры](https://tabun.everypony.ru/blog/Heartstrings/198080.html), и подобных.

Пак составляется из выбранных картинок с дёрпибуры или твайбуры (или других совместимых по API бур) за прошедшие несколько дней (по умолчанию неделя) и постится в черновики в указанный блог. После этого этот черновик нужно открыть, прочекать и опубликовать.

## Как его использовать

1. Проверить, что на машине есть Python 3. Я проверял на 3.7 и 3.8, скорее всего заведётся на любом третьем и может даже на каком-нибудь из вторых, но я не проверял. Для линуксоидов это на 99% так и есть, виндузятникам придётся его [поставить самостоятельно](https://www.python.org/downloads/), если он не стоит. Стоит отметить, что последняя версия, которую можно поставить на семёрку — 3.8, 3.9 ставится только на 8.1 или десятку.

2. Поставить нужные модули, в особенности [tabun_api](https://andreymal.org/tabun/api_doc/main.html) от Андреймала (остальные, скорее всего, уже стоят):
```
pip3 install datetime requests pathlib http3 urllib3 python-dateutil emoji
pip3 install git+https://github.com/andreymal/tabun_api.git#egg=tabun_api[full]
```
Если `pip3` нет, то скорее всего, можно использовать команду `pip` вместо неё: такое бывает, если третий питон — единственный стоящий на машине.

3. Сконфигурировать скрипт (его конфигурация находится в его начале). Те параметры, которые нельзя оставить, как есть, и нужно поменять по сравнению с дефолтной конфигурацией, выделены галочками:

* [x] `username` — логин на табуне.
* [x] `password` — пароль от табуна.
* [ ] `proxy` — прокси, если нужен, иначе просто пустая строка.
* [ ] `mirror` — адрес буры.
* [ ] `apitype` — вариант API сайта: `derpibooru` (для [Derpibooru](https://www.derpibooru.org) и [Trixiebooru](https://www.trixiebooru.org)), `ponerpics` (для [Ponerpics](https://www.ponerpics.org) и [Ponybooru](https://www.ponybooru.org)) или `twibooru` (для [Twibooru](https://www.twibooru.org)).
* [x] `title` — название поста, в нём на место `___` (три подчёркивания) подставится номер пака (начинается с 1 и дальше увеличивается).
* [x] `tags` — теги, которые будут у поста.
* [x] `blog_id` — численный идентификатор блога, куда постить или строка из URL ссылки на блог (например, ЯРОК — это `fanart`, ЗХ — `sketch_drawing`, БПНХ — `draw_help`, СБК — `rough_blog`, награнь — `borderline`). 0 — это персональный блог.
* [x] `pony` — дёрпибурной тег поньки, имени которой мы будем создавать пак.
* [x] `bonuspony` — дёрпибурной тег бонусной поньки (можно сделать несколько "бонусных" спойлеров в конце). Поиск для бонусной поньки ведётся с исключением основной; то есть, если `pony == 'lyra heartstrings'` и `bonuspony == 'bon-bon'`, то в бонусы будут попадать те картинки, на которых есть Бон-Бон, но нету Лиры. Если бонус не нужен, то здесь следует оставить пустую строку.
* [ ] `also` — дополнительные теги.
* [ ] `sort` — параметр для сортировки (`wilson_score`, в отличие от `score`, позволяет встревать годноте, которую тупо видело очень мало народа).
* [ ] `tmpl_body` — шаблон поста. Здесь на место `__OP_PIC__` подставится ОП-пикча, на `__PIC_BLOCK__` — блок картинок в спойлерах, на `___` — номер пака.
* [ ] `tmpl_text_spoiler_header` — шаблон текстового заголовка спойлера.
* [ ] `tmpl_text_spoiler_header_bonus` — шаблон текстового заголовка спойлера бонуса.
* [ ] `tmpl_pic_spoiler_header` — шаблон заголовка спойлера с картинкой.
* [ ] `tmpl_pic_spoiler_header_bonus` — шаблон заголовка спойлера бонуса с картинкой.
* [ ] `tmpl_op_pic` — шаблон ОП-пички.
* [ ] `tmpl_alttext` — шаблон альттекста каждой картинки.
* [ ] `tmpl_spoiler_contents` — шаблон содержимого спойлера.
* [ ] `tmpl_spoiler_contents_bonus` — шаблон содержимого спойлера бонуса.
* [ ] `defaults` — значения подстановок для шаблона, если соответствующих данных о картинке нет.
* [ ] `spoilerpics` — здесь можно указать либо массив ссылок на пикчи, уже загруженные на табун, чтобы получить в заголовках спойлеров такую красоту, как в паках Селестии и Луны; либо просто оставить None или пустой массив, и тогда скрипт сгенерит текстовые заголовки спойлеров. Если будет выбрано больше картинок, чем элементов в этом массиве, то оставшиеся спойлеры будут иметь текстовые заголовки.
* [ ] `bonuspic` — картинка для спойлера бонуса. Опять-таки, либо ссылка на пикчу, уже загруженную на табун, либо None или пустая строка, чтобы создать текстовый спойлер.
* [ ] `timezone` — часовой пояс, для Москвы это `+03:00`.
* [ ] `config` — путь к файлу, где будет храниться номер последнего отправленного пака. Это нужно, чтобы автоматически его увеличивать в заголовке поста. Путь относителен от домашней директории пользователя (`~` в линуксе, и что-то типа `C:\Users\имя_пользователя` в винде). Файл можно редактировать, если нужно сбросить номер пака или, наоборот, переставить его на нужный. Если в файле, например, записана цифра 5, то скрипт отправит пак с номером 6 и изменит цифру в файле на 6. Если файл удалён или отсутствует, то он будет создан, а нумерация паков начнётся с 1.
* [ ] `backup` — путь к файлу, где будет сохранён код поста, если его не удалось запостить на табун. Путь также относителен от домашней директории пользователя.
* [ ] `pick` - путь к pick-файлу, временному файлу для выбора картинок (см. ниже про логику работы скрипта). Путь также относителен от домашней директории пользователя. Также можно указать здесь `'*:rentry'` для загрузки на [rentry.co](https://rentry.co).
* [ ] `period` — количество дней, за которые надо тянуть пикчи с буры (например, 7 — это все пикчи за последнюю неделю).
* [ ] `offset` — смещение вытаскиваемых картинок от текущей даты. `None` — брать самые последние картинки (за последние `period` дней); `{'years': 1}` — картинки годичной давности; `{'months': 6}` — полугодовой; `{'years': 1, 'months': 6, 'days': 15}` — полуторагодовой плюс полмесяца. Поддерживаются ключи `'years'`, `'months'`, `'days'`.
* [ ] `pagelimit` — максимальное количество выкачиваемых страниц буры. `0` — выкачивать все возможные, `1` — вести себя как раньше (выкачивать одну страницу).
* [ ] `pressenter` — `True`, если перед выходом надо попросить нажать ENTER (удобно в случае запуска не из консоли), `False` в противном случае.

В шаблонах (то есть, в переменных, начинающихся на `tmpl_`), кроме `tmpl_body` (у него и у `title` свои переменные, указанные выше), можно использовать следующие подстановки:

* На место `___` подставится номер спойлера (везде, кроме `tmpl_op_pic`).
* На место `__PIC__` подставится URL картинки из `spoilerpics` (только в `tmpl_pic_spoiler_header` и `tmpl_pic_spoiler_header_bonus`).
* На место `__PIC__` подставится URL картинки-превью (только в `tmpl_op_pic`, `tmpl_spoiler_contents` и `tmpl_spoiler_contents_bonus`).
* На место `__FULL__` подставится полная ссылка на хайрез картинки (только в `tmpl_op_pic`, `tmpl_spoiler_contents` и `tmpl_spoiler_contents_bonus`).
* На место `__DESC__` подставится описание картинки на буре, если оно задано (иначе значение из `defaults`).
* На место `__NAME__` подставится название картинки на буре, если оно задано (иначе значение из `defaults`).
* На место `__AUTHOR__` подставится содержимое тега `artist:` после двоеточия, если он есть; иначе ник загрузившего картинку на буру, если он задан; иначе значение из `defaults`.
* На место `__SOURCE__` подставится исходный URL картинки на буре, если он задан (иначе значение из `defaults`).
* На место `__ID__` подставится ID картинки на буре.
* На место `__DB_URL__` подставится URL страницы с картинкой на буре.

4. Запустить скрипт.

Он сделает следующее:

* выкачает блок метаинформации о пикчах на первых `pagelimit` страницах (или обо всех имеющихся, если `limit` равен 0; на каждой странице 50 пикч) с выбранной буры с тегами `pony` и `also` и сортировкой по параметру `sort` (по умолчанию `wilson_score`);
* сделает то же самое, если задана бонусная понька, но с тегами `bonuspony`, `-pony` и `also`;
* создаст pick-файл для выбора лучших пикч со ссылками на эти картинки (после этого этот файл нужно будет открыть в браузере — его URL скрипт выведет в консоль);
* спросит, какие пикчи публиковать; здесь надо ввести (через пробел, запятую или точку с запятой) номера нужных пикч, начиная с ОП-пикчи. Они будут опубликованы в посте именно в том порядке, в котором введены; например, если ввести `3 5 1 2`, то ОП-пикчей станет третья, а потом будут созданы три спойлера с пикчами 5, 1 и 2;
* если задана бонусная понька, то дальше спросит таким же образом номера бонусных пикч (они будут отдельно показаны в pick-файле вторым блоком; будет создано столько бонусных спойлеров, сколько пикч тут будет указано);
* загрузит для ОП-пикчи представления `medium` и `full`, а для всех остальных — `large` и `full` на табун (все неправильно введённые номера будут проигнорированы, а если представление `full` не удастся залить на табун, то будет сделана попытка залить вместо него представление `large`);
* создаст пост, в котором первая небонусная пикча будет ОП-пикчей (КДПВ), а остальные будут запиханы под спойлеры (номерные, а затем бонусные), при этом по клику на каждую пикчу будет открываться (по умолчанию) её полный вариант в новой вкладке, а альттекстом (тоже по умолчанию) будет служить её дескрипшен с буры;
* запостит этот пост на табун в указанный блог в виде черновика;
* если это не удалось, то оставит содержимое поста в виде файла, указанного в переменной `backup`, и его можно будет залить на табун вручную.

После этого останется только залезть в свои черновики, проверить, опубликовать пост и пнуть его в ленту (или, если запостить его не удалось, то разобраться, почему и вручную создать пост с содержимым из backup-файла).

Если `pick` начинается с символов `*:`, то это означает, что pick-файл будет залит на внешний ресурс, указанный после этих символов. Сейчас из таких ресурсов поддерживается `rentry`: если указать это слово после двоеточия, то pick-файл будет создан в формате Markdown и залит на Rentry.

Если же `pick` не начинается с этих символов, то pick-файл будет создан в формате HTML и положен по пути, указанному в этой переменной (относительно домашнего каталога пользователя).

Идея с pick-файлом появилась потому, что автоматический запуск скрипта через `crontab` не оправдал себя — куда удобнее не чистить черновик поста от негодных пикч, а сразу в диалоговом режиме со скриптом указывать ему пикчи для публикации.

Коды возврата:
* 0  — всё отлично, можно лезть в черновики проверять появившийся пост;
* 1  — не получилось импортировать модуль `tabun_api`;
* 2  — не получилось достучаться до буры;
* 3  — не получилось разобрать JSON, который вернула бура;
* 31 — неправильно указан протокол после `*:` в параметре `pick` (сейчас поддерживается только `rentry`);
* 32 — не удалось залить pick-файл на удалённый ресурс ([rentry.co](https://rentry.co));
* 4  — не удалось залогиниться на табун;
* 5  — не удалось залить пикчи на табун;
* 9  — не удалось определить блог по его текстовому имени;
* 10 — не получилось запостить пост на табун.
