const base_url =  "http://127.0.0.1:5000"
var vm = new Vue({
    el: "#box",
    data() {
        return {
            images: [],
            cols:3,
            rows:null
        }
    },
    mounted(){
        this.getFavoriteImages()
    },
    methods: {
        getFavoriteImages()
        {
            axios({
                url: base_url+'/viewMyFavoriteImages',
                method: "Get"
            }).then(resp => {
                this.images = resp.data.data
                this.rows = Math.ceil(this.images.length/this.cols) //向上取整
            })
        },
        removeFavoriteImage(image_name){
            axios({
                url: base_url+'/removeOneFavoriteImage',
                method: "Post",
                data:{
                    image:image_name
                },
                headers:{
                    'Content-Type':'application/json; charset=UTF-8'
                }
            }).then(resp => {
                if(resp.data.code==200){
                    this.ok("已取消收藏")
                    this.images = resp.data.data
                    this.rows = Math.ceil(this.images.length/this.cols) //向上取整
                }else{
                    // 提示不能重复删除
                    this.fail("不必重复删除")
                }
            })
        },
        // 成功提示
        ok(msg) {
            this.$message({
                showClose: true,
                message: msg,
                type: 'success'
            });
        },
        //失败提示
        fail(msg) {
            this.$message({
                showClose: true,
                message: msg,
                type: 'error'
            });
        }
    }
})
