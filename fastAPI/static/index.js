var map; // 지도 객체를 전역 변수로 선언

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(savePosition, showError);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

function savePosition(position) {
    var userLocation = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
    };

    // 사용자 위치를 기반으로 지도 생성
    var mapContainer = document.getElementById('main_map'), // 지도를 표시할 div 
        mapOption = {
            center: new kakao.maps.LatLng(userLocation.latitude, userLocation.longitude), // 지도의 중심좌표
            level: 3 // 지도의 확대 레벨
        };        

    map = new kakao.maps.Map(mapContainer, mapOption); // 지도 객체 초기화

    var marker = new kakao.maps.Marker({
        map: map, 
        position: new kakao.maps.LatLng(userLocation.latitude, userLocation.longitude)
    });
}

function showError(error) {
    console.warn(`ERROR(${error.code}): ${error.message}`);
}

getLocation();

async function changeLocation(pointName) {
    console.log(pointName);
    const response = await fetch(`/location/${pointName}`);    
    const data = await response.json();

    if(map) { // map 객체가 초기화된 경우에만 실행
        var moveLatLon = new kakao.maps.LatLng(data.latitude, data.longitude);
        map.setCenter(moveLatLon);

        var marker = new kakao.maps.Marker({
            map: map, 
            position: new kakao.maps.LatLng(data.latitude, data.longitude)
        });

        var content = '<div class="wrap">' + 
            '    <div class="info">' + 
            '        <div class="title">' + 
            pointName +            
            '            <div class="close" onclick="closeOverlay()" title="닫기"></div>' + 
            '        </div>' + 
            '        <div class="body">' + 
            '            <div class="img">' +
            '                <img src="https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/thumnail.png" width="73" height="70">' +
            '           </div>' + 
            '            <div class="desc">' + 
            '                <div class="ellipsis">제주특별자치도 제주시 첨단로 242</div>' + 
            '                <div class="jibun ellipsis">(우) 63309 (지번) 영평동 2181</div>' + 
            '                <div><a href="https://www.kakaocorp.com/main" target="_blank" class="link">홈페이지</a></div>' + 
            '            </div>' + 
            '        </div>' + 
            '    </div>' +    
            '</div>';

            var overlay = new kakao.maps.CustomOverlay({
                content: content,
                map: map,
                position: marker.getPosition()       
            });

            // 마커를 클릭했을 때 커스텀 오버레이를 표시합니다
            kakao.maps.event.addListener(marker, 'click', function() {
                overlay.setMap(map);
            });

            // 커스텀 오버레이를 닫기 위해 호출되는 함수입니다 
            function closeOverlay() {
                overlay.setMap(null);     
            }




    } else {
        console.log("Map is not initialized");
    }
}