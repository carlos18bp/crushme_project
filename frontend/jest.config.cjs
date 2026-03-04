module.exports = {
    moduleFileExtensions: ['js', 'json', 'vue', 'mjs'],
    transform: {
        '^.+\\.vue$': '@vue/vue3-jest',
        '^.+\\.js$': 'babel-jest',
        '^.+\\.mjs$': 'babel-jest',
        ".+\\.(css|styl|less|sass|scss|png|jpg|webp|ttf|woff|woff2)$": "jest-transform-stub"
    },
    testEnvironment: 'jest-environment-jsdom',
    coverageProvider: 'v8',
    coverageReporters: ['text', 'json-summary'],
    resetModules: true,
    testEnvironmentOptions: {
        customExportConditions: ["node", "node-addons"],
    },
    testMatch: [
        '<rootDir>/test/**/*.test.js',
        '<rootDir>/test/**/*.spec.js',
    ],
    testPathIgnorePatterns: [
        '/node_modules/',
        '/e2e/',
    ],
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
        '\\.(css|less|scss|sass|png|jpg|webp|ttf|woff|woff2)$': 'jest-transform-stub',
    },
    collectCoverageFrom: [
        'src/**/*.{js,vue}',
        '!src/**/main.js',
    ],
    coveragePathIgnorePatterns: [
        '/node_modules/',
        '/e2e/',
    ],
};
