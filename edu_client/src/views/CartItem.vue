<template>
  <div class="cart_item" v-show="show_cart">
    <div class="cart_column column_1">
      <el-checkbox class="my_el_checkbox" v-model="course.selected"></el-checkbox>
    </div>
    <div class="cart_column column_2">
      <img :src="course.course_img" alt="">
      <span><router-link :to="'/detail/'+course.id">{{ course.name }}</router-link></span>
    </div>
    <div class="cart_column column_3">
      <el-select v-model="expire" size="mini" placeholder="请选择购买有效期" class="my_el_select" >
        <el-option :label="item.expire_text" :value="item.id"
                   v-for="(item, index) in course.expire_list" :key="index">
        </el-option>
      </el-select>
    </div>
    <div class="cart_column column_4">¥{{ course.final_price }}</div>
    <div class="cart_column column_4" @click="del_course">删除</div>
  </div>
</template>
<script>
export default {
  name: "CartItem",
  props: ['course'],
  watch: {
    'course.selected': function () {
      // 后台发起请求改变状态
      this.change_select();
    },
    'expire':function () {
      this.change_expire()
    }
  },
  data() {
    return {

      expire:this.course.expire_id,
      // final_price : this.course.final_price,
      show_cart:true,

    }
  },

  methods: {
    change_expire(){
      this.$axios({
        url: this.$settings.HOST + 'cart/option/',
        method:'put',
        data:{
          course_id : this.course.id,
          expire_id : this.expire,
        },
        headers: {
          "Authorization": "jwt " + localStorage.getItem('token'),
        }
      }).then(res=>{
        this.course.final_price = res.data.price;
        console.log(res)
        this.$emit('cart_total_price')
      }).catch(error=>{
        console.log(error)
      })
    },

    del_course(){
      this.$axios({
        url: this.$settings.HOST + 'cart/option/',
        method:'delete',
        data:{
          course_id :this.course.id,
        },
        headers: {
          "Authorization": "jwt " + localStorage.getItem('token'),
        }
      }).then(res=>{
        console.log(77,res.data)
        this.$store.commit("add_cart",res.data.cart_length)
        this.$emit('cart_total_price1')

      }).catch(error=>{
        console.log(error)
      })
    },

    change_select() {
      this.$axios({
        url: this.$settings.HOST + 'cart/option/',
        method:'patch',
        data:{
          course_id :this.course.id,
          selected:this.course.selected,
        },
        headers: {
          "Authorization": "jwt " + localStorage.getItem('token'),
        }
      }).then(res=>{
        this.$message.success(res.data.message);
        this.$emit('cart_total_price')
      }).catch(error=>{

        console.log(error)
      })
    },
  },

}
</script>

<style scoped>
.cart_item::after {
  content: "";
  display: block;
  clear: both;
}

.cart_column {
  float: left;
  height: 250px;
}

.cart_item .column_1 {
  width: 88px;
  position: relative;
}

.my_el_checkbox {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  margin: auto;
  width: 16px;
  height: 16px;
}

.cart_item .column_2 {
  padding: 67px 10px;
  width: 520px;
  height: 116px;
}

.cart_item .column_2 img {
  width: 175px;
  height: 115px;
  margin-right: 35px;
  vertical-align: middle;
}

.cart_item .column_3 {
  width: 197px;
  position: relative;
  padding-left: 10px;
}

.my_el_select {
  width: 117px;
  height: 28px;
  position: absolute;
  top: 0;
  bottom: 0;
  margin: auto;
}

.cart_item .column_4 {
  padding: 67px 10px;
  height: 116px;
  width: 142px;
  line-height: 116px;
}

</style>
