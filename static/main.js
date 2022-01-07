'use strict';

var STORAGE_KEY = "board-game-deals";
// cleanup local storage
localStorage.setItem(STORAGE_KEY, "[]");

var dealsStorage = {
    fetch: function() {
        var deals = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
        deals.forEach(function(deal, index) {
            deals.id = index;
        });
        dealsStorage.uid = deals.length;
        return deals;
    },
    save: function(deals) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(deals));
    }
};


var app = new Vue({
    data: {
        game: "",
        game_info: null,
        deals: dealsStorage.fetch(),
        isLoading: false,
        isEmptyResult: false,
        searchTime: null,
    },
    watch: {
        deals: {
            handler: function(games) {
                dealsStorage.save(games);
            },
            deep: true
        }
    },
    mounted () {
        this.suggestGame()
            .then(res => this.fetchGameInfo());
    },
    computed: {
        // filter by price
        filteredDeals: function() {
            var sorted_deals = [...this.deals];
            sorted_deals.sort(function(a, b) {
                if (!a.price) {
                    return false;
                }
                if (!b.price) {
                    return true;
                }
                return a.price.amount - b.price.amount
            });
            return sorted_deals;
        },
        imageUrl: function() {
            if (!this.game_info) {
                return 'none';
            }
            return 'url(' + '"' + this.game_info.image + '"' + ')';
        }
    },
    methods: {
        searchGame: function() {
            var that = this;
            this.reset();
            var value = this.game && this.game.trim();
            if (!value) {
                return;
            }
            if (this.game_info.name != this.game) {
                this.game_info = null;
                this.fetchGameInfo();
            }
            const evtSource = new EventSource("/api/v1/stream-search/?game=" + value);
            evtSource.addEventListener("update", function(event) {
                console.log(event);
                var new_deals = JSON.parse(event["data"]);
                new_deals.forEach(deal => {
                    that.deals.push({
                        id: dealsStorage.uid++,
                        subject: deal["subject"],
                        description: deal["description"],
                        images: deal["images"],
                        location: deal["location"],
                        owner: deal["owner"],
                        price: deal["price"],
                        source: deal["source"],
                        url: deal["url"],
                        price_converted: deal["price_converted"],
                    });
                });
                that.game = "";
            });
            evtSource.addEventListener("end", function(event) {
                console.log('Handling end....')
                var data = JSON.parse(event["data"]);
                evtSource.close();
                that.isLoading = false;
                that.isEmptyResult = that.deals.length === 0;
                that.searchTime = data["time"];
            });
        },
        reset: function() {
            if (this.deals) {
                this.deals.splice(0, this.deals.length);
            }
            this.searchTime = null;
            this.isLoading = true;
            this.isEmptyResult = false;
        },
        fetchGameInfo: function() {
            var that = this;
            this.game_info = null;
            return axios
                .get("/api/v1/game-info/" + that.game)
                .then(function(response) {
                    that.game_info = response.data;
                    return that.game_info;
                });
        },
        suggestGame: function() {
            var that = this;
            return axios
              .get("/api/v1/game-suggests")
              .then(function(response) {
                    that.game = response.data.game;
                    return that.game;
              });
        }
    }
});
app.$mount("#app-container");
