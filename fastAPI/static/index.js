new Vue({
    el: '#app',
    data() {
        return {
            states: [],
            species: [],
            map: null,
            markers: [],
            fpNames: [],
            latitudes: [],
            longitudes: [],
            addresss:[],
            selectedStates:[],
            selectedSpecie:[],
            selectedFpInfo: null
        };
    },
    async created() {
        await this.fetchStates();
        await this.fetchMarker();
        await this.fetchFpInfo();
    },
    methods: {
        async fetchStates() {
            try {
                const response = await fetch('/state_data');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.states = data.states;
                this.species = data.species;
            } catch (error) {
                console.error('There was an error fetching the states:', error);
            }
        },
        // 좌표 정보 및 리스트 가져오기
        async fetchMarker() {
            try {
                const response = await fetch('/marker_data');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.fpNames = data.fpNames;
                this.latitudes = data.latitudes;
                this.longitudes = data.longitudes;
                this.addresss = data.addresss;
                this.initMap();
            } catch (error) {
                console.error('There was an error fetching the species:', error);
            }
        },

        // 필터링
        async filterData(event) {
            const value = event.target.value;
            const isChecked = event.target.checked;
            const isStateCheckbox = event.target.classList.contains('state-checkbox');
            const isSpeciesCheckbox = event.target.classList.contains('species-checkbox');
            
            if (isStateCheckbox) {
                if (isChecked) {
                    this.selectedStates.push(value);
                } else {
                    const index = this.selectedStates.indexOf(value);
                    if (index > -1) {
                        this.selectedStates.splice(index, 1);
                    }
                }
            }        
            if (isSpeciesCheckbox) {
                if (isChecked) {
                    this.selectedSpecie.push(value);
                } else {
                    const index = this.selectedSpecie.indexOf(value);
                    if (index > -1) {
                        this.selectedSpecie.splice(index, 1);
                    }
                }
            }        
            const stateQueryParams = this.selectedStates.map(state => `states=${encodeURIComponent(state)}`).join('&');
            const speciesQueryParams = this.selectedSpecie.map(specie => `species=${encodeURIComponent(specie)}`).join('&');
            const queryParams = `${stateQueryParams}&${speciesQueryParams}`;
        
            const response = await fetch(`/filter?${queryParams}`, {
                method: 'GET'
            });
            const filteredData = await response.json();
            this.fpNames = filteredData.fpNames;
            this.latitudes = filteredData.latitudes;
            this.longitudes = filteredData.longitudes;
            this.addresss = filteredData.addresss;
            this.initMap();
        },

        initMap() {
            const mapContainer = this.$refs.mapContainer;
            const mapOption = {
                center: new kakao.maps.LatLng(this.latitudes[0], this.longitudes[0]),
                level: 3
            };
            this.map = new kakao.maps.Map(mapContainer, mapOption);

            // 마커 이미지 설정
            const imageSrc = 'static/img/marker.png',
                imageSize = new kakao.maps.Size(64, 69),
                imageOption = { offset: new kakao.maps.Point(27, 69) };
            const markerImage = new kakao.maps.MarkerImage(imageSrc, imageSize, imageOption)            
            
            const positions = this.fpNames.map((name, index) => ({
                content: `<div style="min-width: 250px; width: auto; max-width: 100%; font-family: Arial, sans-serif; border: 1px solid rgba(0,0,0,.1); border-radius: .25rem; background-color: #ffffff; box-shadow: 0 0.25rem 0.75rem rgba(0,0,0,.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: .5rem .75rem; background-color: rgba(0,0,123,.06); border-bottom: 1px solid rgba(0,0,0,.125);">
                  <strong style="font-size: .875rem; color: #007bff; white-space: nowrap;">${name}</strong>
                  <button type="button" style="box-sizing: content-box; width: 1.5em; height: 1.5em; padding: 0; color: #6c757d; border: none; background: transparent; font-size: .875rem; cursor: pointer;" aria-label="Close">            
                  </button>
                </div>
                <div style="padding: .75rem; font-size: .875rem; color: #6c757d; overflow-wrap: break-word;">
                  <span>${this.addresss[index]}</span>
                </div>
            </div>
            `,  // fpNames에서 이름 사용
                latlng: new kakao.maps.LatLng(this.latitudes[index], this.longitudes[index])
            }));
            
            let currentOverlay;

            positions.forEach((position) => {
                const marker = new kakao.maps.Marker({
                    map: this.map,  // Vue.js 데이터 속성에서 지도 객체 사용
                    position: position.latlng,
                    image: markerImage
                });
                const overlay = new kakao.maps.CustomOverlay({                                        
                    content: position.content,
                    position: marker.getPosition(),
                    xAnchor: 0.5,
                    yAnchor: 1.4
                });

                kakao.maps.event.addListener(marker, 'click', () =>{
                    if (currentOverlay) {
                        currentOverlay.setMap(null);
                    }

                    // 클릭된 마커에 해당하는 오버레이를 표시합니다.
                    if (currentOverlay !== overlay) {
                        overlay.setMap(this.map);
                        currentOverlay = overlay; // 현재 활성화된 오버레이를 업데이트합니다.
                    } else {
                        currentOverlay = null; // 오버레이가 이미 활성화된 경우 참조를 제거합니다.
                    }
                });
            });
        },
        
        async fetchFpInfo(fpName) {
            try {
                console.log(fpName)                
                const response = await fetch(`/fp_info/${fpName}`);                              
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.selectedFpInfo = data;
                this.fpName = data.fpName;
                this.latitude = data.latitude;
                this.longitude = data.longitude;
                this.address = data.address;
                
            const mapContainer = this.$refs.mapContainer;
            const mapOption = {
                center: new kakao.maps.LatLng(this.latitude, this.longitude),
                level: 3
            };
            this.map = new kakao.maps.Map(mapContainer, mapOption);

            // 마커 이미지 설정
            const imageSrc = 'static/img/marker.png',
                imageSize = new kakao.maps.Size(64, 69),
                imageOption = { offset: new kakao.maps.Point(27, 69) };
            const markerImage = new kakao.maps.MarkerImage(imageSrc, imageSize, imageOption)            
            

            const marker = new kakao.maps.Marker({
                map: this.map,  // Vue.js 데이터 속성에서 지도 객체 사용
                position: new kakao.maps.LatLng(this.latitude, this.longitude),
                image: markerImage
            });
            const overlay = new kakao.maps.CustomOverlay({                                        
                content: `<div style="min-width: 250px; width: auto; max-width: 100%; font-family: Arial, sans-serif; border: 1px solid rgba(0,0,0,.1); border-radius: .25rem; background-color: #ffffff; box-shadow: 0 0.25rem 0.75rem rgba(0,0,0,.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: .5rem .75rem; background-color: rgba(0,0,123,.06); border-bottom: 1px solid rgba(0,0,0,.125);">
                  <strong style="font-size: .875rem; color: #007bff; white-space: nowrap;">${this.fpName}</strong>
                  <button type="button" style="box-sizing: content-box; width: 1.5em; height: 1.5em; padding: 0; color: #6c757d; border: none; background: transparent; font-size: .875rem; cursor: pointer;" aria-label="Close">            
                  </button>
                </div>
                <div style="padding: .75rem; font-size: .875rem; color: #6c757d; overflow-wrap: break-word;">
                  <span>${this.address}</span>
                </div>
            </div>
            `,
                position: marker.getPosition(),
                xAnchor: 0.5,
                yAnchor: 1.4
            });            
            let currentOverlay;
            kakao.maps.event.addListener(marker, 'click', () =>{
                if (currentOverlay) {
                    currentOverlay.setMap(null);
                }
                if (currentOverlay !== overlay) {
                    overlay.setMap(this.map);
                    currentOverlay = overlay;
                } else {
                    currentOverlay = null;
                }
          });

            } catch (error) {
                console.error('There was an error fetching the states:', error);
            }
        }
        
    }
});
