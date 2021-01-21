# Docker OSM server

Для работы необходимо поместить каталоги db и bin в папку resources.

В файле resources/osm/settings.yml заменить адреса server_url и overpass_url на актуальный адрес хоста, на котором будет запущен контейнер.

    server_url: "192.168.4.132:8080/osm_tiles/"
    overpass_url: "https://192.168.4.132:9090/api/interpreter"


В файле resources/mod_tile/index.html заменить адрес на актуальный адрес хоста, на котором будет запущен контейнер.

    L.tileLayer('http://192.168.4.132:8080/osm_tiles/{z}/{x}/{y}.png',{maxZoom:18}).addTo(map);


(npospelov/test - в качестве примера имени)

Создание образа: `docker build -t npospelov/test .`

Запуск: `docker run --name osm -p 8080:80 -p 9090:8080 -p 3003:3000 -it npospelov/test`


