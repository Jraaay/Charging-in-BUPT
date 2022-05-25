<template>
  <div class="floatButton" v-if="token != ''">
    <el-popover placement="bottom" :width="200" trigger="click" class="gm">
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
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-popover>
  </div>
  <el-container>
    <el-header>
      <el-row>
        <el-col :span="3">
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
        </el-col>
        <el-col :span="12">
          <div class="title">巴普特充电系统</div>
        </el-col>
        <el-col :span="9">
          <div class="user-icon" v-if="token != ''">
            <svg
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
        </el-col>
      </el-row>
    </el-header>
    <el-main class="main" v-if="token != ''">
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
        <div class="state-remain-time">预计还需：{{ remainTime }}</div>
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
          @click="reqChargeDialog = true"
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
            :loading="buttonLoading[operations.indexOf(i)]"
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
    <span>请选择您的充电模式</span>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="reqChargeDialog = false"
          >快充</el-button
        >
        <el-button type="primary" @click="reqChargeDialog = false"
          >慢充</el-button
        >
        <el-button @click="reqChargeDialog = false">取消</el-button>
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
      <el-descriptions border :column="1">
        <el-descriptions-item label="详单编号" align="center">
          114514
        </el-descriptions-item>
        <el-descriptions-item label="详单生成时间" align="center">
          1919-08-10 11:45:14
        </el-descriptions-item>
        <el-descriptions-item label="充电桩编号" align="center">
          6
        </el-descriptions-item>
        <el-descriptions-item label="充电电量" align="center">
          120度
        </el-descriptions-item>
        <el-descriptions-item label="充电时长" align="center">
          2小时37分10秒
        </el-descriptions-item>
        <el-descriptions-item label="启动时间" align="center">
          1919-08-10 11:45:14
        </el-descriptions-item>
        <el-descriptions-item label="停止时间" align="center">
          1919-08-10 11:45:14
        </el-descriptions-item>
        <el-descriptions-item label="充电费用" align="center">
          10.35元
        </el-descriptions-item>
        <el-descriptions-item label="服务费用" align="center">
          1.03元
        </el-descriptions-item>
        <el-descriptions-item label="总费用" align="center">
          11.38元
        </el-descriptions-item>
      </el-descriptions>
      <div style="color: #909399; padding-top: 5px">*仅显示上一个详单</div>
    </span>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="showDetail = false">OK</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ElMessage } from "element-plus";
export default {
  name: "App",
  setup() {},
  data() {
    const allOpt = [
      {
        name: "查看详单",
        handler: () => {
          this.buttonLoading[0] = true;
          setTimeout(() => {
            this.buttonLoading[0] = false;
            this.showDetail = true;
          }, 1000);
        },
      },
      {
        name: "修改充电请求",
        handler: () => {
          ElMessage.success("修改充电请求");
        },
      },
      {
        name: "取消充电",
        handler: () => {
          ElMessage.success("取消充电");
        },
      },
      {
        name: "完成充电",
        handler: () => {
          ElMessage.success("完成充电");
        },
      },
      {
        name: "查看费用规则",
        handler: () => {
          this.showFee = true;
        },
      },
    ];
    const operations = [0, 1, 2, 4].map((i) => allOpt[i]);
    return {
      nowCharging: true,
      chargingNo: "F114",
      curStep: "在排队区等候",
      curStateId: 1,
      curState: "正在排队区等候",
      nextStep: "进入充电等候区",
      remainTime: "51分钟",
      remainCarNum: 4,
      token: localStorage.getItem("token") ?? "",
      reqChargeDialog: false,
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
    };
  },
  methods: {
    switchLoginRegister() {
      this.loginOrRegister = !this.loginOrRegister;
    },
    login() {
      ElMessage.success("登录成功");
      localStorage.setItem("token", "123");
      this.token = "123";
    },
    register() {
      ElMessage.success("注册成功");
      localStorage.setItem("token", "123");
      this.token = "123";
    },
    logout() {
      ElMessage.success("退出成功");
      localStorage.removeItem("token");
      this.token = "";
      this.loginOrRegister = true;
      this.loginForm = {
        username: "",
        password: "",
        passwordAgain: "",
      };
    },
  },
  watch: {
    curStateId(val) {
      if (this.curStateId == 0) {
        this.nowCharging = false;
      } else {
        this.nowCharging = true;
      }
      const stateMap = {
        0: ["", "", "", [0, 4]],
        1: ["正在排队区等候", "进入充电区等候", "在排队区等候", [0, 1, 2, 4]],
        2: ["正在充电区等候", "进行充电", "进入充电区并等候", [0, 2, 4]],
        3: ["正在充电", "完成充电", "进行充电", [0, 3, 4]],
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
}
.el-dialog {
  max-width: 600px;
}
</style>
