import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'tests',workers:1,use:{baseURL:'http://127.0.0.1:8000',browserName:'chromium',launchOptions:{executablePath:process.env.PASSERINE_CHROMIUM}},reporter:'list'});
