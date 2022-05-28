module.exports = {
    productionSourceMap: false,
    css: {
        extract: false,
    },
    devServer: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:4523/mock/1046159',
            },
        },
    },
}
