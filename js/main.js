import routes from './routes.js';
import { store } from './store.js';

const app = Vue.createApp({
    data: () => ({ store }),
    async created() {
        await store.loadSettings();
    }
});
const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes,
});

app.use(router);

app.mount('#app');
