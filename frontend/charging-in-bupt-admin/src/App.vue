<template>
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
          <div class="title">巴普特充电管理系统</div>
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
      <el-space wrap>
        <div>
          <el-button
            type="primary"
            @click="checkCharger"
            size="large"
            :loading="checkChargerButtonLoading"
          >
            查看充电桩状态
          </el-button>
        </div>
        <div>
          <el-button
            type="primary"
            @click="showReportFunc"
            size="large"
            :loading="showReportButtonLoading"
          >
            查看报表
          </el-button>
        </div>
        <div>
          <el-button
            type="primary"
            @click="showQueueFunc"
            size="large"
            :loading="showQueueButtonLoading"
          >
            查看排队信息
          </el-button>
        </div>
      </el-space>
    </el-main>
    <el-main class="main" v-if="token == ''">
      <div class="card-header">
        <h1>登录</h1>
      </div>
      <el-form
        ref="loginForm"
        :model="loginForm"
        label-width="80px"
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
      </el-form>
      <el-button type="primary" @click="login"> 登录 </el-button>
    </el-main>
  </el-container>
  <el-dialog
    v-model="showChargerStatus"
    title="查看充电桩状态"
    width="90%"
    center
  >
    <span>
      <el-table :data="piles_stat" stripe style="width: 100%">
        <el-table-column prop="pile_id" label="id" width="60" />
        <el-table-column
          prop="status"
          label="状态"
          :filter-method="filterTag"
          :filters="[
            { text: '运行中', value: 'MAINTAINING' },
            { text: '已关闭', value: 'SHUTDOWN' },
            { text: '故障', value: 'UNAVAILABLE' },
          ]"
        >
          <template #default="scope">
            <el-tag
              disable-transitions
              :type="
                scope.row.status === 'MAINTAINING'
                  ? 'success'
                  : scope.row.status === 'SHUTDOWN'
                  ? 'info'
                  : 'danger'
              "
            >
              {{ statusMap[scope.row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cumulative_usage_times" label="使用次数" />
        <el-table-column
          prop="cumulative_charging_time"
          label="充电时间（h）"
        />
        <el-table-column
          prop="cumulative_charging_amount"
          label="充电电量（Ah）"
        />
        <el-table-column fixed="right" label="操作" width="60">
          <template #default="scope">
            <el-button
              text
              size="small"
              type="primary"
              style="padding: 0"
              @click="changeStatus(scope.row)"
              >设置</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </span>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="showChargerStatus = false">OK</el-button>
      </span>
    </template>
  </el-dialog>
  <el-dialog
    v-model="showReport"
    title="查看充电桩状态"
    width="90%"
    center
    @close="
      {
        selectedReport = null;
        selectedReportId = null;
      }
    "
  >
    <span>
      <div style="margin-bottom: 15px">
        查看报表
        <el-cascader
          v-model="selectedReportId"
          :options="reports"
          @change="handleReportChange"
        />
      </div>
      <el-descriptions border :column="1" v-if="selectedReport">
        <el-descriptions-item label="月" align="center">
          {{ selectedReport.month }}
        </el-descriptions-item>
        <el-descriptions-item label="周" align="center">
          {{ selectedReport.week }}
        </el-descriptions-item>
        <el-descriptions-item label="天" align="center">
          {{ selectedReport.day }}
        </el-descriptions-item>
        <el-descriptions-item label="充电桩编号" align="center">
          {{ selectedReport.pile_id }}
        </el-descriptions-item>
        <el-descriptions-item label="累计使用次数" align="center">
          {{ selectedReport.cumulative_usage_times }}
        </el-descriptions-item>
        <el-descriptions-item label="累计充电量" align="center">
          {{ selectedReport.cumulative_charging_amount }}
        </el-descriptions-item>
        <el-descriptions-item label="累计充电费用" align="center">
          {{ selectedReport.cumulative_charging_earning }}
        </el-descriptions-item>
        <el-descriptions-item label="累计服务费用" align="center">
          {{ selectedReport.cumulative_service_earning }}
        </el-descriptions-item>
        <el-descriptions-item label="累计总费用" align="center">
          {{ selectedReport.cumulative_earning }}
        </el-descriptions-item>
      </el-descriptions>
    </span>
    <template #footer> </template>
  </el-dialog>
  <el-dialog
    v-model="showSelectChargerStatus"
    title="选择充电桩状态"
    width="300px"
    center
  >
    <span> 请选择需要修改的状态 </span>
    <template #footer>
      <span class="dialog-footer">
        <el-button
          :loading="selectChargerStatusButtonLoading[0]"
          @click="confirmChangeChargerStatus('MAINTAINING')"
          plain
          type="primary"
          >开启</el-button
        >
        <el-button
          :loading="selectChargerStatusButtonLoading[1]"
          @click="confirmChangeChargerStatus('SHUTDOWN')"
          plain
          type="info"
          >关闭</el-button
        >
        <el-button
          :loading="selectChargerStatusButtonLoading[2]"
          @click="confirmChangeChargerStatus('UNAVAILABLE')"
          plain
          type="danger"
          >故障</el-button
        >
      </span>
    </template>
  </el-dialog>
  <el-dialog
    v-model="showQueue"
    title="查看排队信息"
    width="90%"
    center
    @close="
      {
        selectedQueue = null;
        selectedQueueId = null;
      }
    "
  >
    <span>
      <div style="margin-bottom: 15px">
        查看报表
        <el-cascader
          v-model="selectedQueueId"
          :options="queues"
          @change="handleQueueChange"
        />
      </div>
      <el-descriptions border :column="1" v-if="selectedQueue">
        <el-descriptions-item label="充电桩编号" align="center">
          {{ selectedQueue.pile_id }}
        </el-descriptions-item>
        <el-descriptions-item label="用户编号" align="center">
          {{ selectedQueue.user_id }}
        </el-descriptions-item>
        <el-descriptions-item label="电池容量（单位：Ah）" align="center">
          {{ selectedQueue.battery_size }}
        </el-descriptions-item>
        <el-descriptions-item label="请求充电量（单位：Ah）" align="center">
          {{ selectedQueue.require_amount }}
        </el-descriptions-item>
        <el-descriptions-item label="已等待时间（单位：秒）" align="center">
          {{ selectedQueue.waiting_time }}
        </el-descriptions-item>
      </el-descriptions>
    </span>
    <template #footer> </template>
  </el-dialog>
</template>

<script>
import { ElMessage, ElLoading } from "element-plus";
import axios from "axios";
export default {
  name: "App",
  data() {
    return {
      loginForm: {
        username: "",
        password: "",
        passwordAgain: "",
      },
      token: localStorage.getItem("token"),
      checkChargerButtonLoading: false,
      showReportButtonLoading: false,
      showQueueButtonLoading: false,
      piles_stat: [],
      showChargerStatus: false,
      showReport: false,
      showQueue: false,
      showSelectChargerStatus: false,
      changeChargerId: "",
      reports: [],
      reportsRaw: [],
      queues: [],
      queuesRaw: [],
      selectChargerStatusButtonLoading: [false, false, false],
      statusMap: {
        MAINTAINING: "运行中",
        SHUTDOWN: "已关闭",
        UNAVAILABLE: "故障",
      },
      props: {
        expandTrigger: "hover",
      },
      selectedReportId: null,
      selectedReport: null,
      selectedQueueId: null,
      selectedQueue: null,
    };
  },
  methods: {
    login() {
      const loading = ElLoading.service({
        fullscreen: true,
        text: "登录中...",
        background: "rgba(255, 255, 255, 1)",
      });
      axios
        .post("/api/user/login", {
          username: this.loginForm.username,
          password: this.loginForm.password,
        })
        .then((res) => {
          if (res.data.code === 0) {
            const token = res.data.data.token;
            if (res.data.is_admin) {
              this.token = token;
              localStorage.setItem("token", token);
              loading.close();
              ElMessage.success("登录成功");
            } else {
              ElMessage.error("您不是管理员");
              loading.close();
            }
          } else {
            ElMessage.error(res.data.message);
          }
        });
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
    checkCharger() {
      this.checkChargerButtonLoading = true;
      axios
        .get("/api/admin/query_all_piles_stat")
        .then((res) => {
          if (res.data.code === 0) {
            this.piles_stat = res.data.data;
            this.showChargerStatus = true;
            ElMessage.success("查询成功");
          } else {
            ElMessage.error(res.data.message);
          }
          this.checkChargerButtonLoading = false;
        })
        .catch((err) => {
          ElMessage.error(err);
          this.checkChargerButtonLoading = false;
        });
    },
    filterTag: (value, row) => {
      return row.status === value;
    },
    showReportFunc() {
      this.showReportButtonLoading = true;
      axios.get("/api/admin/query_report").then((res) => {
        if (res.data.code === 0) {
          const data = res.data.data;
          this.reportsRaw = data;
          const reports = [];
          for (let i = 0; i < data.length; i++) {
            const month = data[i].month;
            const day = data[i].day;
            const charger_id = data[i].pile_id;
            reports[month] = reports[month] ?? {
              value: month,
              label: month + "月",
              children: [],
            };
            reports[month].children.push({
              value: day,
              label: day + "日",
              children: [],
            });
            // reports[month].children.find((item) => item.value === day)
            reports[month].children[
              reports[month].children.indexOf(
                reports[month].children.find((item) => item.value === day)
              )
            ].children.push({
              value: charger_id,
              label: charger_id + "充电桩",
            });
          }
          this.reports = [];
          for (const key in reports) {
            this.reports.push(reports[key]);
          }
          this.showReport = true;
          console.log(this.reports);
          ElMessage.success("查询成功");
        } else {
          ElMessage.error(res.data.message);
        }
        this.showReportButtonLoading = false;
      });
      // .catch((err) => {
      //   ElMessage.error(err);
      //   this.showReportButtonLoading = false;
      // });
    },
    changeStatus(row) {
      this.changeChargerId = row.pile_id;
      this.showSelectChargerStatus = true;
    },
    confirmChangeChargerStatus(status) {
      this.selectChargerStatusButtonLoading[
        status == "MAINTAINING" ? 0 : status == "SHUTDOWN" ? 1 : 2
      ] = true;
      axios
        .post("/api/admin/update_pile", {
          charger_id: this.changeChargerId,
          status: status,
        })
        .then((res) => {
          if (res.data.code === 0) {
            ElMessage.success("修改成功");
            this.showSelectChargerStatus = false;
            this.showChargerStatus = false;
          } else {
            ElMessage.error(res.data.message);
          }
          this.selectChargerStatusButtonLoading[
            status == "MAINTAINING" ? 0 : status == "SHUTDOWN" ? 1 : 2
          ] = false;
        })
        .catch((err) => {
          ElMessage.error(err);
        });
    },
    handleReportChange() {
      this.selectedReport = this.reportsRaw.find(
        (item) =>
          item.month == this.selectedReportId[0] &&
          item.day == this.selectedReportId[1]
      );
      console.log(this.reportsRaw);
      console.log(this.selectedReport);
    },
    showQueueFunc() {
      this.showQueueButtonLoading = true;
      axios
        .get("/api/admin/query_queue")
        .then((res) => {
          if (res.data.code === 0) {
            const data = res.data.data;
            this.queueRaw = data;
            console.log(data);
            const queues = [];
            for (let i = 0; i < data.length; i++) {
              const charger_id = data[i].pile_id;
              queues[charger_id] = queues[charger_id] ?? {
                value: charger_id,
                label: charger_id + "充电桩",
                children: [],
              };
              queues[charger_id].children.push({
                value: data[i].user_id,
                label: data[i].user_id + "用户",
              });
            }
            this.queues = [];
            for (const key in queues) {
              this.queues.push(queues[key]);
            }
            this.showQueue = true;
            ElMessage.success("查询成功");
          } else {
            ElMessage.error(res.data.message);
          }
          this.showQueueButtonLoading = false;
        })
        .catch((err) => {
          ElMessage.error(err);
          this.showQueueButtonLoading = false;
        });
    },
    handleQueueChange() {
      console.log(this.queueRaw);
      console.log(this.selectedQueueId);
      this.selectedQueue = this.queueRaw.find(
        (item) =>
          item.pile_id == this.selectedQueueId[0] &&
          item.user_id == this.selectedQueueId[1]
      );
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
.loginForm {
  max-width: 400px;
}
.user-icon {
  padding-top: 20px;
  text-align: right;
}
tr.el-table__row {
  text-align-last: center;
}
table.el-table__header {
  text-align-last: center;
}
.el-dialog {
  max-width: 450px;
}
</style>
