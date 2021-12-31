/**


**/
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
        deals: dealsStorage.fetch(),
        isLoading: false,
        isEmptyResult: false,
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
        axios
          .get("/api/v1/games-suggests")
          .then(response => (this.game = response.data.game))
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
    },
    methods: {
        searchGame: function() {
            this.cleanupGames();
            var value = this.game && this.game.trim();
            if (!value) {
                return;
            }
            this.isLoading = true;
            this.isEmptyResult = false;
            const evtSource = new EventSource("/api/v1/stream/games?game=" + value);
            var that = this;
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
                this.game = "";
            });
            evtSource.addEventListener("end", function(event) {
                console.log('Handling end....')
                evtSource.close();
                that.isLoading = false;
                that.isEmptyResult = that.deals.length === 0;
            });
        },
        cleanupGames: function() {
            if (this.deals) {
                this.deals.splice(0, this.deals.length);
            }
        }
    }
});
app.$mount(".app-container");
