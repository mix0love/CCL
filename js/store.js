import { fetchSettings } from './content.js';

export const store = Vue.reactive({
    dark: JSON.parse(localStorage.getItem('dark')) || false,
    settings: {
        title: "CCL - GDPS List",
        primary_color: "#003366",
        telegram_link: "https://t.me/cclistnews",
        submit_link: "https://docs.google.com/forms/d/e/1FAIpQLSfJKdsbsAvUe38iWvChERO7ot3MRWlrlHShNqpKwu-KNA5AOw/viewform",
        list_name_header: "CCL"
    },
    toggleDark() {
        this.dark = !this.dark;
        localStorage.setItem('dark', JSON.stringify(this.dark));
    },
    async loadSettings() {
        const s = await fetchSettings();
        if (s) {
            this.settings = { ...this.settings, ...s };
            document.title = this.settings.title;
            // Update CSS var
            document.documentElement.style.setProperty('--color-primary', this.settings.primary_color);
        }
    }
});
