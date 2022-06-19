const base_url =  "http://127.0.0.1:5000"
var vm = new Vue({
    delimiters: ["##", "##"],
    el: "#box",
    data() {
        return {
            file:null,
            images:[],
            cols:3,
            rows:0,
            k:9, //一次性查询的数量
            tag_list:[],
            loading: false, //加载
            options:[
                {value:9},
                {value:18},
                {value:27},
                {value:36},
            ],
            checkbox:[
                "animals","baby","bird","car","clouds",
                "dog","female","flower","food","indoor","lake",
                "male","night","people","plant_life","portrait",
                "river","sea","sky","structures","sunset","transport",
                "tree","water"
            ]

        }
    },
    mounted(){
        image_str = localStorage.getItem("images")
        if(image_str!==null){
            this.images = image_str.split(',')
            this.rows = Math.ceil(this.images.length/this.cols) //向上取整
        }
    },
    methods:{
        async uploadFile(){
            if(this.file==null){
                this.fail("请先上传一张图片")
                return
            }
            if(this.k<=0||this.k>2955){
                this.fail("搜索的数量超出范围，建议选择 1~2955 之间的值")
                return
            }
            this.loading = true
            let formData = new FormData()
            formData.append('file',this.file.raw)
            formData.append('k',this.k)
            formData.append('tag_list',this.tag_list)
            axios({
                url: base_url+'/imgUpload',
                method: "Post",
                data:formData,
            }).then(resp => {
                if(resp.data.code==200){
                    this.images = resp.data.data
                    this.rows = Math.ceil(this.images.length/this.cols) //向上取整
                    localStorage.setItem("images",this.images)  //存到本地
                }
                this.loading = false
            }).catch(resp => {
                this.fail("网络出错，请检查后端服务是否开启")
            })
        },
        async addFavoriteImage(image_name){
            axios({
                url: base_url+'/addOneFavoriteImage',
                method: "Post",
                data:{
                    image:image_name
                }
            }).then(resp => {
                if(resp.data.code==200){
                    this.ok("收藏成功，可以在‘收藏夹’查看收藏的图片")
                }else{
                    this.fail(resp.data.message)
                }
            })
        },
        async clear(){
            this.images=[]
            this.rows=0
            localStorage.removeItem("images")
        },
        change(file, fileList){
            this.file = file
        },
        handleRemove(file, fileList) {
            this.file = null
        },
        handlePreview(file) {
            console.log(file);
        },
        submitUpload() {
            if(this.file==null){
                this.fail("请先上传一张图片")
            }
            else{
                this.$refs.upload.submit();
            }
        },
        onExceed(file,fileList){
            this.fail("一次最多上传一张图片")
        },
        // 成功提示
        async ok(msg) {
            this.$message({
                showClose: true,
                message: msg,
                type: 'success'
            });
        },
        //失败提示
        async fail(msg) {
            this.$message({
                showClose: true,
                message: msg,
                type: 'error'
            });
        }
      }
    })