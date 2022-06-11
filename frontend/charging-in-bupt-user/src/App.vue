<template>
  <div class="floatButton" v-if="token != ''">
    <el-popover placement="bottom" :width="250" trigger="click" class="gm">
      <template #reference>
        <el-icon :size="25" color="white"><Setting /></el-icon>
      </template>
      <el-form>
        <el-form-item label="当前状态">
          <el-radio-group v-model="curStateId" size="small">
            <el-radio-button label="0" />
            <el-radio-button label="1" />
            <el-radio-button label="2" />
            <el-radio-button label="3" />
            <el-radio-button label="4" />
            <el-radio-button label="5" />
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-popover>
  </div>
  <el-container>
    <el-header>
      <el-row style="display: flex; justify-content: space-between">
        <svg
          t="1653482435664"
          class="icon"
          viewBox="0 0 1109 1024"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          p-id="2385"
          width="30"
          height="30"
          style="margin-top: 15px; margin-right: 5px"
        >
          >
          <path
            d="M1066.666667 341.333333h-42.666667v405.333334a149.333333 149.333333 0 0 1-298.666667 0V298.666667a42.666667 42.666667 0 0 0-42.666666-42.666667v682.666667h85.333333v85.333333H0v-85.333333h85.333333V85.333333a85.333333 85.333333 0 0 1 85.333334-85.333333h426.666666a85.333333 85.333333 0 0 1 85.333334 85.333333v85.333334a128 128 0 0 1 128 128v448a64 64 0 0 0 128 0V341.333333h-42.666667a42.666667 42.666667 0 0 1-42.666667-42.666666V213.333333a42.666667 42.666667 0 0 1 42.666667-42.666666v-21.333334a21.333333 21.333333 0 0 1 42.666667 0V170.666667h85.333333v-21.333334a21.333333 21.333333 0 0 1 42.666667 0V170.666667a42.666667 42.666667 0 0 1 42.666666 42.666666v85.333334a42.666667 42.666667 0 0 1-42.666666 42.666666zM341.333333 810.666667l170.666667-170.666667H384v-128l-128 170.666667h128z m256-682.666667H170.666667v256h426.666666V128z m426.666667 85.333333h-85.333333a42.666667 42.666667 0 0 0 0 85.333334h85.333333a42.666667 42.666667 0 0 0 0-85.333334z"
            p-id="2386"
            fill="#ffffff"
          ></path>
        </svg>
        <div class="title">巴普特充电系统</div>
        <div class="user-icon">
          <svg
            v-if="token != ''"
            t="1653485792064"
            class="icon"
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            p-id="3294"
            width="20"
            height="20"
            @click="logout"
            style="cursor: pointer"
          >
            <path
              d="M1024 512l-100.937143 103.424-0.731428-0.768L768 770.596571l-103.497143-103.460571L746.422857 585.142857H329.142857v-146.285714h417.28l-81.92-82.029714L768 253.403429l154.331429 155.940571 0.731428-0.804571zM109.714286 182.857143v658.285714a73.142857 73.142857 0 0 0 73.142857 73.142857h365.714286v109.714286H146.285714a146.285714 146.285714 0 0 1-146.285714-146.285714V146.285714a146.285714 146.285714 0 0 1 146.285714-146.285714h402.285715v109.714286H182.857143a73.142857 73.142857 0 0 0-73.142857 73.142857z"
              p-id="3295"
              fill="#ffffff"
            ></path>
          </svg>
        </div>
      </el-row>
    </el-header>
    <el-main class="main" v-if="token != ''">
      <div style="margin-bottom: 15px">
        当前时间：<el-tag>{{ curTime }}</el-tag>
      </div>
      <el-card class="box-card" v-if="nowCharging">
        <template #header>
          <div class="card-header">
            <span>
              排队号：<el-tag>{{ chargingNo }}</el-tag>
            </span>
          </div>
        </template>
        <div>
          <el-tag size="large">{{ curState }}</el-tag>
        </div>
        <div class="state-remain-time">现在您该：{{ curStep }}</div>
        <div class="state-remain-time">下一步：{{ nextStep }}</div>
        <div class="state-remain-time">
          该模式前面还有：{{ remainCarNum }}辆车
        </div>
      </el-card>
      <el-card class="box-card" v-if="!nowCharging">
        <template #header>
          <div class="card-header">
            <span><el-tag type="info">当前没有充电请求</el-tag></span>
          </div>
        </template>
        <el-button
          class="reqCharge"
          type="primary"
          @click="reqChargeDialogFunc"
        >
          请求充电
        </el-button>
      </el-card>
      <el-divider />
      <el-space wrap>
        <div v-for="i in operations" :key="i">
          <el-button
            type="primary"
            @click="i.handler"
            size="large"
            :loading="buttonLoading[i.id]"
          >
            {{ i.name }}
          </el-button>
        </div>
      </el-space>
    </el-main>
    <el-main class="main" v-if="token == ''">
      <div class="card-header">
        <h1 v-if="loginOrRegister">登录</h1>
        <h1 v-if="!loginOrRegister">注册</h1>
      </div>
      <el-form
        ref="loginForm"
        :model="loginForm"
        label-width="80px"
        :rules="rules"
        class="loginForm"
      >
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="loginForm.password"
            type="password"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item
          label="重复密码"
          v-if="!loginOrRegister"
          prop="passwordAgain"
        >
          <el-input
            v-model="loginForm.passwordAgain"
            type="password"
            show-password
          ></el-input>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="login" v-if="loginOrRegister">
        登录
      </el-button>
      <el-button type="primary" @click="register" v-if="!loginOrRegister">
        注册
      </el-button>
      <el-button link @click="switchLoginRegister" v-if="!loginOrRegister">
        返回登录
      </el-button>
      <el-button link @click="switchLoginRegister" v-if="loginOrRegister">
        注册
      </el-button>
    </el-main>
  </el-container>
  <el-dialog v-model="reqChargeDialog" title="选择充电模式" width="90%" center>
    <span>
      <el-form :model="reqChargeForm" label-width="120px" label-position="top">
        <el-form-item label="充电模式">
          <el-radio-group v-model="reqChargeForm.charge_mode">
            <el-radio-button label="快充" />
            <el-radio-button label="慢充" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="请求充电量">
          <el-input-number
            v-model="reqChargeForm.require_amount"
            :min="1"
            :precision="2"
          />（单位：Wh）
        </el-form-item>
        <el-form-item label="电池容量">
          <el-input-number
            v-model="reqChargeForm.battery_size"
            :min="1"
            :precision="2"
          />（单位：Wh）
        </el-form-item>
      </el-form>
    </span>
    <template #footer>
      <span class="dialog-footer">
        <el-button
          type="primary"
          @click="reqChargeFunc"
          :loading="chargeReqLoading"
          >请求</el-button
        >
        <el-button @click="reqChargeDialog = false">取消</el-button>
      </span>
    </template>
  </el-dialog>
  <el-dialog
    v-model="reqChangeChargeDialog"
    title="修改充电模式"
    width="90%"
    center
  >
    <span>
      <el-form
        :model="reqChangeChargeForm"
        label-width="120px"
        label-position="top"
      >
        <el-form-item label="充电模式">
          <el-radio-group v-model="reqChangeChargeForm.charge_mode">
            <el-radio-button label="快充" />
            <el-radio-button label="慢充" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="请求充电量">
          <el-input-number
            v-model="reqChangeChargeForm.require_amount"
            :min="1"
          />（单位：Wh）
        </el-form-item>
      </el-form>
    </span>
    <template #footer>
      <span class="dialog-footer">
        <el-button
          type="primary"
          @click="reqChangeChargeFunc"
          :loading="chargeReqLoading"
          >修改</el-button
        >
        <el-button @click="reqChangeChargeDialog = false">取消</el-button>
      </span>
    </template>
  </el-dialog>
  <el-dialog v-model="showFee" title="查看费用规则" width="90%" center>
    <span>
      <el-table :data="feeData" stripe style="width: 100%">
        <el-table-column prop="time" label="时间" />
        <el-table-column prop="fee" label="价格" />
      </el-table>
    </span>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="showFee = false">OK</el-button>
      </span>
    </template>
  </el-dialog>
  <el-dialog v-model="showDetail" title="查看详单" width="90%" center>
    <span>
      <div style="margin-bottom: 15px">
        选择订单号：
        <el-select v-model="selectedOrder" placeholder="选择订单">
          <el-option
            v-for="item in order_list"
            :key="item.order_id"
            :label="item.order_id"
            :value="order_list.indexOf(item)"
          />
        </el-select>
      </div>
      <el-descriptions border :column="1">
        <el-descriptions-item label="详单编号" align="center">
          {{ order_list[selectedOrder].order_id }}
        </el-descriptions-item>
        <el-descriptions-item label="详单生成时间" align="center">
          {{ order_list[selectedOrder].create_time }}
        </el-descriptions-item>
        <el-descriptions-item label="充电桩编号" align="center">
          {{ order_list[selectedOrder].pile_id }}
        </el-descriptions-item>
        <el-descriptions-item label="充电电量" align="center">
          {{ order_list[selectedOrder].charged_amount }} Wh
        </el-descriptions-item>
        <el-descriptions-item label="充电时长" align="center">
          {{
            order_list[selectedOrder].charged_time / 3600 >= 1
              ? Math.floor(order_list[selectedOrder].charged_time / 3600) +
                " 小时"
              : ""
          }}
          {{
            (order_list[selectedOrder].charged_time % 3600) / 60 >= 1
              ? Math.floor(
                  (order_list[selectedOrder].charged_time % 3600) / 60
                ) + " 分钟"
              : ""
          }}
          {{ order_list[selectedOrder].charged_time % 60 }} 秒
        </el-descriptions-item>
        <el-descriptions-item label="启动时间" align="center">
          {{ order_list[selectedOrder].begin_time }}
        </el-descriptions-item>
        <el-descriptions-item label="停止时间" align="center">
          {{ order_list[selectedOrder].end_time }}
        </el-descriptions-item>
        <el-descriptions-item label="充电费用" align="center">
          {{ order_list[selectedOrder].charging_cost }} 元
        </el-descriptions-item>
        <el-descriptions-item label="服务费用" align="center">
          {{ order_list[selectedOrder].service_cost }} 元
        </el-descriptions-item>
        <el-descriptions-item label="总费用" align="center">
          {{ order_list[selectedOrder].total_cost }} 元
        </el-descriptions-item>
      </el-descriptions>
    </span>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="showDetail = false">OK</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ElMessage, ElMessageBox, ElLoading } from "element-plus";
import axios from "axios";
export default {
  name: "App",
  created() {
    if (localStorage.getItem("token")) {
      const token = localStorage.getItem("token");
      const loading = ElLoading.service({
        fullscreen: true,
        text: "正在加载...",
        background: "rgba(255, 255, 255, 1)",
      });
      setTimeout(() => {
        axios
          .get("/api/user/preview_queue", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
          .then((res) => {
            if (res.data.code === 0) {
              const stateMap = {
                NOTCHARGING: 0,
                WAITINGSTAGE1: 1,
                WAITINGSTAGE2: 2,
                CHARGING: 3,
                CHANGEMODEREQUEUE: 4,
                FAULTREQUEUE: 5,
              };
              this.chargingNo = res.data.data.charge_id;
              this.remainCarNum = res.data.data.queue_len;
              this.curStateId = stateMap[res.data.data.cur_state];
              this.place = res.data.data.place;
              loading.close();
              ElMessage.success("加载成功");
            } else {
              ElMessage.error(res.data.message);
              loading.close();
            }
          })
          .catch((err) => {
            ElMessage.error(err);
            loading.close();
          });
      }, 0);
      this.startTimer();
    }
  },
  data() {
    const allOpt = [
      {
        id: 0,
        name: "查看详单",
        handler: () => {
          this.buttonLoading[0] = true;
          axios
            .get("/api/user/query_order_detail", {
              headers: {
                Authorization: `Bearer ${this.token}`,
              },
            })
            .then((res) => {
              if (res.data.code === 0) {
                this.buttonLoading[0] = false;
                this.order_list = res.data.data;
                this.selectedOrder = 0;
                if (this.order_list.length === 0) {
                  ElMessage.warning("暂无详单");
                  this.buttonLoading[0] = false;
                } else {
                  // sort this.order_list
                  this.order_list.sort((a, b) => {
                    return b.order_id - a.order_id;
                  });
                  this.showDetail = true;
                }
              } else {
                this.buttonLoading[0] = false;
                ElMessage.error(res.data.message);
              }
            })
            .catch((err) => {
              this.buttonLoading[0] = false;
              ElMessage.error(err);
            });
        },
      },
      {
        id: 1,
        name: "修改充电请求",
        handler: () => {
          this.reqChangeChargeDialogFunc();
        },
      },
      {
        id: 2,
        name: "取消充电",
        handler: () => {
          this.buttonLoading[2] = true;
          axios
            .get("/api/user/end_charging_request", {
              headers: {
                Authorization: `Bearer ${this.token}`,
              },
            })
            .then((res) => {
              if (res.data.code === 0) {
                ElMessage.success("取消成功");
                this.refreshState();
              } else {
                ElMessage.error(res.data.message);
              }
              this.buttonLoading[2] = false;
            })
            .catch((err) => {
              ElMessage.error(err);
              this.buttonLoading[2] = false;
            });
        },
      },
      {
        id: 3,
        name: "完成充电",
        handler: () => {
          this.buttonLoading[3] = true;
          axios
            .get("/api/user/end_charging_request", {
              headers: {
                Authorization: `Bearer ${this.token}`,
              },
            })
            .then((res) => {
              if (res.data.code === 0) {
                ElMessage.success("完成充电");
                this.refreshState();
              } else {
                ElMessage.error(res.data.message);
              }
              this.buttonLoading[3] = false;
            })
            .catch((err) => {
              ElMessage.error(err);
              this.buttonLoading[3] = false;
            });
        },
      },
      {
        id: 4,
        name: "查看费用规则",
        handler: () => {
          this.showFee = true;
        },
      },
    ];
    const operations = [0, 1, 2, 4].map((i) => allOpt[i]);
    return {
      timeConfig: {
        startTime: null,
        timeSpeed: null,
        startRealTime: null,
      },
      timer1: null,
      timer2: null,
      nowCharging: false,
      chargingNo: "",
      curStep: "",
      curStateId: 0,
      curState: "",
      nextStep: "",
      order_list: [
        {
          begin_time: "1986-09-15 14:43:40",
          create_time: "1995-12-13 04:15:21",
          service_cost: 87,
          charged_time: 1605705295379,
          total_cost: 92,
          order_id: "26",
          charged_amount: 17,
          charging_cost: 96,
          end_time: "2016-07-30 23:59:14",
        },
      ],
      place: "",
      remainCarNum: 4,
      token: localStorage.getItem("token") ?? "",
      chargeReqLoading: false,
      reqChargeDialog: false,
      reqChangeChargeDialog: false,
      showFee: false,
      showDetail: false,
      allOpt: allOpt,
      operations: operations,
      buttonLoading: [false, false, false, false, false],
      loginForm: {
        username: "",
        password: "",
        passwordAgain: "",
      },
      loginOrRegister: true,
      rules: {
        passwordAgain: [
          {
            validator: (rule, value, callback) => {
              if (value === "") {
                callback(new Error("请再次输入密码"));
              } else if (value !== this.loginForm.password) {
                callback(new Error("两次输入密码不一致"));
              } else {
                callback();
              }
            },
          },
        ],
      },
      feeData: [
        {
          time: "7:00~10:00",
          fee: "0.7元/度",
        },
        {
          time: "10:00~15:00",
          fee: "1.0元/度",
        },
        {
          time: "15:00~18:00",
          fee: "0.7元/度",
        },
        {
          time: "18:00~21:00",
          fee: "1.0元/度",
        },
        {
          time: "21:00~23:00",
          fee: "0.7元/度",
        },
        {
          time: "23:00~次日7:00",
          fee: "0.4元/度",
        },
      ],
      selectedOrder: 0,
      reqChargeForm: {
        charge_mode: "快充",
        require_amount: "0",
        battery_size: "0",
      },
      reqChangeChargeForm: {
        charge_mode: "快充",
        require_amount: "0",
        battery_size: "0",
      },
      curTime: "2022-06-07 12:34:56",
    };
  },
  methods: {
    switchLoginRegister() {
      this.loginOrRegister = !this.loginOrRegister;
    },
    login() {
      const loading = ElLoading.service({
        fullscreen: true,
        text: "登录中...",
        background: "rgba(255, 255, 255, 1)",
      });
      axios
        .post("/api/login", {
          username: this.loginForm.username,
          password: this.loginForm.password,
        })
        .then((res) => {
          if (res.data.code === 0) {
            const token = res.data.data.token;
            axios
              .get("/api/user/preview_queue", {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              })
              .then((res) => {
                if (res.data.code === 0) {
                  const stateMap = {
                    NOTCHARGING: 0,
                    WAITINGSTAGE1: 1,
                    WAITINGSTAGE2: 2,
                    CHARGING: 3,
                    CHANGEMODEREQUEUE: 4,
                    FAULTREQUEUE: 5,
                  };
                  this.token = token;
                  localStorage.setItem("token", token);
                  this.chargingNo = res.data.data.charge_id;
                  this.remainCarNum = res.data.data.queue_len;
                  this.curStateId = stateMap[res.data.data.cur_state];
                  this.place = res.data.data.place;
                  loading.close();
                  ElMessage.success("登录成功");
                  this.startTimer();
                } else {
                  ElMessage.error(res.data.message);
                  loading.close();
                }
              })
              .catch((err) => {
                ElMessage.error(err);
                loading.close();
              });
          } else {
            ElMessage.error(res.data.message);
            loading.close();
          }
        });
    },
    register() {
      axios
        .post("/api/user/register", {
          username: this.loginForm.username,
          password: this.loginForm.password,
          re_password: this.loginForm.passwordAgain,
        })
        .then((res) => {
          if (res.data.code === 0) {
            ElMessage.success("注册成功，请登录");
            this.loginOrRegister = true;
          } else {
            ElMessage.error(res.data.message);
          }
        });
    },
    logout() {
      ElMessage.success("退出成功");
      localStorage.removeItem("token");
      this.stopTimer();
      this.token = "";
      this.loginOrRegister = true;
      this.loginForm = {
        username: "",
        password: "",
        passwordAgain: "",
      };
    },
    reqChargeDialogFunc() {
      this.reqChargeForm = {
        charge_mode: "快充",
        require_amount: 0,
        battery_size: 0,
      };
      this.reqChargeDialog = true;
    },
    reqChargeFunc() {
      this.chargeReqLoading = true;
      axios
        .post(
          "/api/user/submit_charging_request",
          {
            charge_mode: this.reqChargeForm.charge_mode == "快充" ? "F" : "T",
            require_amount: this.reqChargeForm.require_amount
              .toFixed(2)
              .toString(),
            battery_size: this.reqChargeForm.battery_size.toFixed(2).toString(),
          },
          {
            headers: {
              Authorization: `Bearer ${this.token}`,
            },
          }
        )
        .then((res) => {
          if (res.data.code === 0) {
            ElMessage.success("请求充电成功");
            this.chargeReqLoading = false;
            this.reqChargeDialog = false;
            this.refreshState();
          } else {
            ElMessage.error(res.data.message);
            this.chargeReqLoading = false;
          }
        })
        .catch((err) => {
          ElMessage.error(err);
          this.chargeReqLoading = false;
        });
    },
    reqChangeChargeDialogFunc() {
      this.reqChangeChargeForm = {
        charge_mode: "快充",
        require_amount: "0",
        battery_size: "0",
      };
      this.reqChangeChargeDialog = true;
    },
    reqChangeChargeFunc() {
      this.chargeReqLoading = true;
      axios
        .post(
          "/api/user/edit_charging_request",
          {
            charge_mode:
              this.reqChangeChargeForm.charge_mode == "快充" ? "F" : "T",
            require_amount: this.reqChangeChargeForm.require_amount.toString(),
          },
          {
            headers: {
              Authorization: `Bearer ${this.token}`,
            },
          }
        )
        .then((res) => {
          if (res.data.code === 0) {
            ElMessage.success("修改充电请求成功");
            this.chargeReqLoading = false;
            this.reqChangeChargeDialog = false;
            this.refreshState();
          } else {
            ElMessage.error(res.data.message);
            this.chargeReqLoading = false;
          }
        });
    },
    startTimer() {
      if (this.timer1) {
        clearInterval(this.timer1);
      }
      if (this.timer2) {
        clearInterval(this.timer2);
      }
      this.timer1 = setInterval(() => {
        this.refreshState();
      }, 1000);
      this.timer2 = setInterval(() => {
        this.refreshTime();
      }, 1000);
    },
    stopTimer() {
      if (this.timer1) {
        clearInterval(this.timer1);
      }
      if (this.timer2) {
        clearInterval(this.timer2);
      }
    },
    refreshState() {
      const token = this.token;
      if (token) {
        axios
          .get("/api/user/preview_queue", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
          .then((res) => {
            if (res.data.code === 0) {
              const stateMap = {
                NOTCHARGING: 0,
                WAITINGSTAGE1: 1,
                WAITINGSTAGE2: 2,
                CHARGING: 3,
                CHANGEMODEREQUEUE: 4,
                FAULTREQUEUE: 5,
              };
              this.chargingNo = res.data.data.charge_id;
              this.remainCarNum = res.data.data.queue_len;
              this.curStateId = stateMap[res.data.data.cur_state];
              this.place = res.data.data.place;
              if (this.curStateId == 2) {
                this.curStep = `进入${this.place}号充电桩并等候`;
              } else if (this.curStateId == 3) {
                this.curStep = `在${this.place}号充电桩进行充电`;
              } else if (this.curStateId == 5) {
                this.curStep = `由于充电桩故障，请进入${this.place}号充电桩并等候`;
              }
            } else {
              ElMessage.error(res.data.message);
            }
          })
          .catch((err) => {
            ElMessage.error(err);
          });
      }
    },
    refreshTime() {
      axios
        .get("/api/time")
        .then((res) => {
          if (res.data.code === 0) {
            this.curTime = res.data.data.datetime;
            console.log(this);
            if (res.data.data.speed != null) {
              this.timeConfig.timeSpeed = res.data.data.speed;
              this.timeConfig.startTime = res.data.data.timestamp;
              this.timeConfig.startRealTime = new Date().getTime() / 1000;
              clearInterval(this.timer2);
              this.timer2 = setInterval(() => {
                const dur =
                  new Date().getTime() / 1000 - this.timeConfig.startRealTime;
                console.log(
                  new Date().getTime() / 1000,
                  this.timeConfig.startRealTime,
                  dur
                );
                const curTime =
                  this.timeConfig.timeSpeed * dur + this.timeConfig.startTime;
                this.curTime = new Date(curTime * 1000).toLocaleString();
              }, 10);
            }
          } else {
            ElMessage.error(res.data.message);
          }
        })
        .catch((err) => {
          ElMessage.error(err);
        });
    },
  },
  watch: {
    curStateId(val, old) {
      console.log(old, val);
      if (old != 0 && val != 0) {
        ElMessageBox.alert("状态已更新，请注意您需要做的动作", "状态更新提醒", {
          confirmButtonText: "好的",
        });
      }
      if (val == 0) {
        this.nowCharging = false;
      } else {
        this.nowCharging = true;
      }
      const stateMap = {
        0: ["", "", "", [0, 4]],
        1: ["正在等候区等候", "进入充电区等候", "在等候区等候", [0, 1, 2, 4]],
        2: [
          "正在充电区等候",
          "进行充电",
          `进入${this.place}号充电桩并等候`,
          [0, 2, 4],
        ],
        3: [
          "正在充电",
          "完成充电",
          `在${this.place}号充电桩进行充电`,
          [0, 3, 4],
        ],
        4: [
          "正在等候区等候",
          "进入充电区等候",
          "由于修改了充电请求，请重新进入等候区等候",
          [0, 1, 2, 4],
        ],
        5: [
          "正在充电区等候",
          "进行充电",
          `由于充电桩故障，请进入${this.place}号充电桩并等候`,
          [0, 2, 4],
        ],
      };
      this.curState = stateMap[val][0];
      this.nextStep = stateMap[val][1];
      this.curStep = stateMap[val][2];
      this.operations = stateMap[val][3].map((i) => this.allOpt[i]);
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
.el-header {
  background: #409eff;
  color: white;
  width: 100%;
}
.title {
  height: 100%;
  line-height: 60px;
  text-align: left;
  font-size: 18px;
}
.main {
  text-align: -webkit-center;
}
.box-card {
  width: 80%;
  max-width: 400px;
}
.state-remain-time {
  margin-top: 10px;
  font-size: 14px;
}
.user-icon {
  padding-top: 20px;
  text-align: right;
  width: 20px;
}
.loginForm {
  max-width: 400px;
}
.floatButton {
  position: fixed;
  right: 60px;
  top: 10px;
  cursor: pointer;
  padding-top: 7px;
  z-index: 99;
}
.reqCharge {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  font-size: 16px;
  margin: 25px;
}
.el-dialog {
  max-width: 450px;
}
</style>
