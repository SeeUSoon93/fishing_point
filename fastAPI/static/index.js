const sqlite3 = require('sqlite3').verbose();

var userLocation = {
    latitude: null,
    longitude: null
};

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(savePosition);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

function savePosition(position) {
    userLocation.latitude = position.coords.latitude;
    userLocation.longitude = position.coords.longitude;
}
getLocation();

// db연결
const db = new sqlite3.Database('./fishing_db.db', sqlite3.OPEN_READONLY, (err) => {
    if (err) {
        return console.error(err.message);
    }
    console.log('db연결');
});

// fishingPoint에서 pointName으로 조회
db.get(`SELECT pointIdx, pointName, address, locationCate, xCoordi, yCoordi, pointInfo, stateName, cityName FROM fishingPoint WHERE pointName = ?`, ['공현진방파제'], (err, row) => {
    if (err) {
        return console.error(err.message);
    }
    if (row) {
        userLocation.latitude = row.xCoordi
        userLocation.longitude = row.yCoordi
        
        console.log(`pointIdx: ${row.pointIdx}`);
        // fishAtPoint에서 해당 pointIdx로 fishIdx 조회
        db.all(`SELECT fishIdx FROM fishAtPoint WHERE pointIdx = ?`, [row.pointIdx], (err, rows) => {
            if (err) {
                return console.error(err.message);
            }
            // fishSpecies에서 fishIdx로 fishName 조회
            rows.forEach((row) => {
                db.get(`SELECT fishName FROM fishSpecies WHERE fishIdx = ?`, [row.fishIdx], (err, fishRow) => {
                    if (err) {
                        return console.error(err.message);
                    }
                    console.log(`fishName: ${fishRow.fishName}`);
                });
            });
        });
    } else {
        console.log('No results found.');
    }

});

var mapContainer = document.getElementById('main_map'), // 지도를 표시할 div 
mapOption = {
    center: new kakao.maps.LatLng(userLocation.latitude, userLocation.longitude), // 지도의 중심좌표
    level: 11 // 지도의 확대 레벨
};

var map = new kakao.maps.Map(mapContainer, mapOption);



// db 연결 종료
db.close((err) => {
    if (err) {
        return console.error(err.message);
    }
    console.log('db종료');
});
