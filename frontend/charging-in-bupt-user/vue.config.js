module.exports = {
  productionSourceMap: false,
  css: {
    extract: false,
  },
  devServer: {
    proxy: {
      "/api": {
        target: "https://cib.jray.xyz/",
      },
    },
  },
};
