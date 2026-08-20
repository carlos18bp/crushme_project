module.exports = {
    moduleFileExtensions: ['js', 'mjs', 'json', 'vue'],
    transform: {
        '^.+\\.vue$': '@vue/vue3-jest',
        '^.+\\.(js|mjs)$': 'babel-jest',
        ".+\\.(css|styl|less|sass|scss|png|jpg|webp|ttf|woff|woff2)$": "jest-transform-stub"
    },
    testEnvironment: 'jest-environment-jsdom',
    coverageProvider: 'v8',
    coverageReporters: ['text', 'json-summary'],
    clearMocks: true,
    restoreMocks: true,
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
        '\\.(css|less|scss|sass|png|jpg|webp|ttf|woff|woff2)$': 'identity-obj-proxy',
    },
    transformIgnorePatterns: ['/node_modules/(?!.*perfect-debounce)'],
    setupFilesAfterEnv: ['./jest.setup.js'],
    collectCoverageFrom: [
        'src/**/*.{js,vue}',
        '!src/**/main.js',
    ],
    coveragePathIgnorePatterns: [
        '/node_modules/',
        '/e2e/',
    ],
};
