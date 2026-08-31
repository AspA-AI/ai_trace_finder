/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "app/api/investigations/[...path]/route";
exports.ids = ["app/api/investigations/[...path]/route"];
exports.modules = {

/***/ "(rsc)/./app/api/investigations/[...path]/route.js":
/*!***************************************************!*\
  !*** ./app/api/investigations/[...path]/route.js ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   GET: () => (/* binding */ GET),\n/* harmony export */   POST: () => (/* binding */ POST),\n/* harmony export */   PUT: () => (/* binding */ PUT)\n/* harmony export */ });\n/* harmony import */ var _lib_backend__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../../../lib/backend */ \"(rsc)/./lib/backend.js\");\n\nasync function forward(request, { params }) {\n    const resolved = await params;\n    return (0,_lib_backend__WEBPACK_IMPORTED_MODULE_0__.proxyRequest)(request, `/investigations/${(resolved.path || []).join(\"/\")}`);\n}\nconst GET = forward;\nconst POST = forward;\nconst PUT = forward;\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9hcHAvYXBpL2ludmVzdGlnYXRpb25zL1suLi5wYXRoXS9yb3V0ZS5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7O0FBQXVEO0FBRXZELGVBQWVDLFFBQVFDLE9BQU8sRUFBRSxFQUFFQyxNQUFNLEVBQUU7SUFDeEMsTUFBTUMsV0FBVyxNQUFNRDtJQUN2QixPQUFPSCwwREFBWUEsQ0FBQ0UsU0FBUyxDQUFDLGdCQUFnQixFQUFFLENBQUNFLFNBQVNDLElBQUksSUFBSSxFQUFFLEVBQUVDLElBQUksQ0FBQyxNQUFNO0FBQ25GO0FBRU8sTUFBTUMsTUFBTU4sUUFBUTtBQUNwQixNQUFNTyxPQUFPUCxRQUFRO0FBQ3JCLE1BQU1RLE1BQU1SLFFBQVEiLCJzb3VyY2VzIjpbIi9Vc2Vycy9yemFwcC9Eb2N1bWVudHMvQXtzcH1BL2FpX3RyYWNlL2Zyb250ZW5kL2FwcC9hcGkvaW52ZXN0aWdhdGlvbnMvWy4uLnBhdGhdL3JvdXRlLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IHByb3h5UmVxdWVzdCB9IGZyb20gXCIuLi8uLi8uLi8uLi9saWIvYmFja2VuZFwiO1xuXG5hc3luYyBmdW5jdGlvbiBmb3J3YXJkKHJlcXVlc3QsIHsgcGFyYW1zIH0pIHtcbiAgY29uc3QgcmVzb2x2ZWQgPSBhd2FpdCBwYXJhbXM7XG4gIHJldHVybiBwcm94eVJlcXVlc3QocmVxdWVzdCwgYC9pbnZlc3RpZ2F0aW9ucy8keyhyZXNvbHZlZC5wYXRoIHx8IFtdKS5qb2luKFwiL1wiKX1gKTtcbn1cblxuZXhwb3J0IGNvbnN0IEdFVCA9IGZvcndhcmQ7XG5leHBvcnQgY29uc3QgUE9TVCA9IGZvcndhcmQ7XG5leHBvcnQgY29uc3QgUFVUID0gZm9yd2FyZDtcbiJdLCJuYW1lcyI6WyJwcm94eVJlcXVlc3QiLCJmb3J3YXJkIiwicmVxdWVzdCIsInBhcmFtcyIsInJlc29sdmVkIiwicGF0aCIsImpvaW4iLCJHRVQiLCJQT1NUIiwiUFVUIl0sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(rsc)/./app/api/investigations/[...path]/route.js\n");

/***/ }),

/***/ "(rsc)/./lib/backend.js":
/*!************************!*\
  !*** ./lib/backend.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   proxyRequest: () => (/* binding */ proxyRequest)\n/* harmony export */ });\nconst BACKEND_URL = process.env.BACKEND_URL || \"http://127.0.0.1:8000\";\nasync function proxyRequest(request, path) {\n    const incoming = new URL(request.url);\n    const url = `${BACKEND_URL}${path}${incoming.search}`;\n    const hasBody = ![\n        \"GET\",\n        \"HEAD\"\n    ].includes(request.method);\n    const upstream = await fetch(url, {\n        method: request.method,\n        headers: filterHeaders(request.headers),\n        body: hasBody ? await request.arrayBuffer() : undefined,\n        duplex: hasBody ? \"half\" : undefined\n    });\n    return new Response(upstream.body, {\n        status: upstream.status,\n        headers: filterResponseHeaders(upstream.headers)\n    });\n}\nfunction filterHeaders(headers) {\n    const out = new Headers();\n    for (const [key, value] of headers.entries()){\n        if ([\n            \"host\",\n            \"connection\",\n            \"content-length\"\n        ].includes(key.toLowerCase())) continue;\n        out.set(key, value);\n    }\n    return out;\n}\nfunction filterResponseHeaders(headers) {\n    const out = new Headers();\n    for (const [key, value] of headers.entries()){\n        if ([\n            \"transfer-encoding\",\n            \"connection\",\n            \"content-length\"\n        ].includes(key.toLowerCase())) continue;\n        out.set(key, value);\n    }\n    return out;\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9saWIvYmFja2VuZC5qcyIsIm1hcHBpbmdzIjoiOzs7O0FBQUEsTUFBTUEsY0FBY0MsUUFBUUMsR0FBRyxDQUFDRixXQUFXLElBQUk7QUFFeEMsZUFBZUcsYUFBYUMsT0FBTyxFQUFFQyxJQUFJO0lBQzlDLE1BQU1DLFdBQVcsSUFBSUMsSUFBSUgsUUFBUUksR0FBRztJQUNwQyxNQUFNQSxNQUFNLEdBQUdSLGNBQWNLLE9BQU9DLFNBQVNHLE1BQU0sRUFBRTtJQUNyRCxNQUFNQyxVQUFVLENBQUM7UUFBQztRQUFPO0tBQU8sQ0FBQ0MsUUFBUSxDQUFDUCxRQUFRUSxNQUFNO0lBQ3hELE1BQU1DLFdBQVcsTUFBTUMsTUFBTU4sS0FBSztRQUNoQ0ksUUFBUVIsUUFBUVEsTUFBTTtRQUN0QkcsU0FBU0MsY0FBY1osUUFBUVcsT0FBTztRQUN0Q0UsTUFBTVAsVUFBVSxNQUFNTixRQUFRYyxXQUFXLEtBQUtDO1FBQzlDQyxRQUFRVixVQUFVLFNBQVNTO0lBQzdCO0lBQ0EsT0FBTyxJQUFJRSxTQUFTUixTQUFTSSxJQUFJLEVBQUU7UUFDakNLLFFBQVFULFNBQVNTLE1BQU07UUFDdkJQLFNBQVNRLHNCQUFzQlYsU0FBU0UsT0FBTztJQUNqRDtBQUNGO0FBRUEsU0FBU0MsY0FBY0QsT0FBTztJQUM1QixNQUFNUyxNQUFNLElBQUlDO0lBQ2hCLEtBQUssTUFBTSxDQUFDQyxLQUFLQyxNQUFNLElBQUlaLFFBQVFhLE9BQU8sR0FBSTtRQUM1QyxJQUFJO1lBQUM7WUFBUTtZQUFjO1NBQWlCLENBQUNqQixRQUFRLENBQUNlLElBQUlHLFdBQVcsS0FBSztRQUMxRUwsSUFBSU0sR0FBRyxDQUFDSixLQUFLQztJQUNmO0lBQ0EsT0FBT0g7QUFDVDtBQUVBLFNBQVNELHNCQUFzQlIsT0FBTztJQUNwQyxNQUFNUyxNQUFNLElBQUlDO0lBQ2hCLEtBQUssTUFBTSxDQUFDQyxLQUFLQyxNQUFNLElBQUlaLFFBQVFhLE9BQU8sR0FBSTtRQUM1QyxJQUFJO1lBQUM7WUFBcUI7WUFBYztTQUFpQixDQUFDakIsUUFBUSxDQUFDZSxJQUFJRyxXQUFXLEtBQUs7UUFDdkZMLElBQUlNLEdBQUcsQ0FBQ0osS0FBS0M7SUFDZjtJQUNBLE9BQU9IO0FBQ1QiLCJzb3VyY2VzIjpbIi9Vc2Vycy9yemFwcC9Eb2N1bWVudHMvQXtzcH1BL2FpX3RyYWNlL2Zyb250ZW5kL2xpYi9iYWNrZW5kLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImNvbnN0IEJBQ0tFTkRfVVJMID0gcHJvY2Vzcy5lbnYuQkFDS0VORF9VUkwgfHwgXCJodHRwOi8vMTI3LjAuMC4xOjgwMDBcIjtcblxuZXhwb3J0IGFzeW5jIGZ1bmN0aW9uIHByb3h5UmVxdWVzdChyZXF1ZXN0LCBwYXRoKSB7XG4gIGNvbnN0IGluY29taW5nID0gbmV3IFVSTChyZXF1ZXN0LnVybCk7XG4gIGNvbnN0IHVybCA9IGAke0JBQ0tFTkRfVVJMfSR7cGF0aH0ke2luY29taW5nLnNlYXJjaH1gO1xuICBjb25zdCBoYXNCb2R5ID0gIVtcIkdFVFwiLCBcIkhFQURcIl0uaW5jbHVkZXMocmVxdWVzdC5tZXRob2QpO1xuICBjb25zdCB1cHN0cmVhbSA9IGF3YWl0IGZldGNoKHVybCwge1xuICAgIG1ldGhvZDogcmVxdWVzdC5tZXRob2QsXG4gICAgaGVhZGVyczogZmlsdGVySGVhZGVycyhyZXF1ZXN0LmhlYWRlcnMpLFxuICAgIGJvZHk6IGhhc0JvZHkgPyBhd2FpdCByZXF1ZXN0LmFycmF5QnVmZmVyKCkgOiB1bmRlZmluZWQsXG4gICAgZHVwbGV4OiBoYXNCb2R5ID8gXCJoYWxmXCIgOiB1bmRlZmluZWQsXG4gIH0pO1xuICByZXR1cm4gbmV3IFJlc3BvbnNlKHVwc3RyZWFtLmJvZHksIHtcbiAgICBzdGF0dXM6IHVwc3RyZWFtLnN0YXR1cyxcbiAgICBoZWFkZXJzOiBmaWx0ZXJSZXNwb25zZUhlYWRlcnModXBzdHJlYW0uaGVhZGVycyksXG4gIH0pO1xufVxuXG5mdW5jdGlvbiBmaWx0ZXJIZWFkZXJzKGhlYWRlcnMpIHtcbiAgY29uc3Qgb3V0ID0gbmV3IEhlYWRlcnMoKTtcbiAgZm9yIChjb25zdCBba2V5LCB2YWx1ZV0gb2YgaGVhZGVycy5lbnRyaWVzKCkpIHtcbiAgICBpZiAoW1wiaG9zdFwiLCBcImNvbm5lY3Rpb25cIiwgXCJjb250ZW50LWxlbmd0aFwiXS5pbmNsdWRlcyhrZXkudG9Mb3dlckNhc2UoKSkpIGNvbnRpbnVlO1xuICAgIG91dC5zZXQoa2V5LCB2YWx1ZSk7XG4gIH1cbiAgcmV0dXJuIG91dDtcbn1cblxuZnVuY3Rpb24gZmlsdGVyUmVzcG9uc2VIZWFkZXJzKGhlYWRlcnMpIHtcbiAgY29uc3Qgb3V0ID0gbmV3IEhlYWRlcnMoKTtcbiAgZm9yIChjb25zdCBba2V5LCB2YWx1ZV0gb2YgaGVhZGVycy5lbnRyaWVzKCkpIHtcbiAgICBpZiAoW1widHJhbnNmZXItZW5jb2RpbmdcIiwgXCJjb25uZWN0aW9uXCIsIFwiY29udGVudC1sZW5ndGhcIl0uaW5jbHVkZXMoa2V5LnRvTG93ZXJDYXNlKCkpKSBjb250aW51ZTtcbiAgICBvdXQuc2V0KGtleSwgdmFsdWUpO1xuICB9XG4gIHJldHVybiBvdXQ7XG59XG4iXSwibmFtZXMiOlsiQkFDS0VORF9VUkwiLCJwcm9jZXNzIiwiZW52IiwicHJveHlSZXF1ZXN0IiwicmVxdWVzdCIsInBhdGgiLCJpbmNvbWluZyIsIlVSTCIsInVybCIsInNlYXJjaCIsImhhc0JvZHkiLCJpbmNsdWRlcyIsIm1ldGhvZCIsInVwc3RyZWFtIiwiZmV0Y2giLCJoZWFkZXJzIiwiZmlsdGVySGVhZGVycyIsImJvZHkiLCJhcnJheUJ1ZmZlciIsInVuZGVmaW5lZCIsImR1cGxleCIsIlJlc3BvbnNlIiwic3RhdHVzIiwiZmlsdGVyUmVzcG9uc2VIZWFkZXJzIiwib3V0IiwiSGVhZGVycyIsImtleSIsInZhbHVlIiwiZW50cmllcyIsInRvTG93ZXJDYXNlIiwic2V0Il0sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(rsc)/./lib/backend.js\n");

/***/ }),

/***/ "(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&page=%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute.js&appDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=!":
/*!***********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&page=%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute.js&appDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=! ***!
  \***********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   patchFetch: () => (/* binding */ patchFetch),\n/* harmony export */   routeModule: () => (/* binding */ routeModule),\n/* harmony export */   serverHooks: () => (/* binding */ serverHooks),\n/* harmony export */   workAsyncStorage: () => (/* binding */ workAsyncStorage),\n/* harmony export */   workUnitAsyncStorage: () => (/* binding */ workUnitAsyncStorage)\n/* harmony export */ });\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next/dist/server/route-modules/app-route/module.compiled */ \"(rsc)/./node_modules/next/dist/server/route-modules/app-route/module.compiled.js\");\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! next/dist/server/route-kind */ \"(rsc)/./node_modules/next/dist/server/route-kind.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! next/dist/server/lib/patch-fetch */ \"(rsc)/./node_modules/next/dist/server/lib/patch-fetch.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var _Users_rzapp_Documents_A_sp_A_ai_trace_frontend_app_api_investigations_path_route_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./app/api/investigations/[...path]/route.js */ \"(rsc)/./app/api/investigations/[...path]/route.js\");\n\n\n\n\n// We inject the nextConfigOutput here so that we can use them in the route\n// module.\nconst nextConfigOutput = \"\"\nconst routeModule = new next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__.AppRouteRouteModule({\n    definition: {\n        kind: next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__.RouteKind.APP_ROUTE,\n        page: \"/api/investigations/[...path]/route\",\n        pathname: \"/api/investigations/[...path]\",\n        filename: \"route\",\n        bundlePath: \"app/api/investigations/[...path]/route\"\n    },\n    distDir: \".next-dev\" || 0,\n    projectDir:  false || '',\n    resolvedPagePath: \"/Users/rzapp/Documents/A{sp}A/ai_trace/frontend/app/api/investigations/[...path]/route.js\",\n    nextConfigOutput,\n    userland: _Users_rzapp_Documents_A_sp_A_ai_trace_frontend_app_api_investigations_path_route_js__WEBPACK_IMPORTED_MODULE_3__\n});\n// Pull out the exports that we need to expose from the module. This should\n// be eliminated when we've moved the other routes to the new format. These\n// are used to hook into the route.\nconst { workAsyncStorage, workUnitAsyncStorage, serverHooks } = routeModule;\nfunction patchFetch() {\n    return (0,next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__.patchFetch)({\n        workAsyncStorage,\n        workUnitAsyncStorage\n    });\n}\n\n\n//# sourceMappingURL=app-route.js.map//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9ub2RlX21vZHVsZXMvbmV4dC9kaXN0L2J1aWxkL3dlYnBhY2svbG9hZGVycy9uZXh0LWFwcC1sb2FkZXIvaW5kZXguanM/bmFtZT1hcHAlMkZhcGklMkZpbnZlc3RpZ2F0aW9ucyUyRiU1Qi4uLnBhdGglNUQlMkZyb3V0ZSZwYWdlPSUyRmFwaSUyRmludmVzdGlnYXRpb25zJTJGJTVCLi4ucGF0aCU1RCUyRnJvdXRlJmFwcFBhdGhzPSZwYWdlUGF0aD1wcml2YXRlLW5leHQtYXBwLWRpciUyRmFwaSUyRmludmVzdGlnYXRpb25zJTJGJTVCLi4ucGF0aCU1RCUyRnJvdXRlLmpzJmFwcERpcj0lMkZVc2VycyUyRnJ6YXBwJTJGRG9jdW1lbnRzJTJGQSU3QnNwJTdEQSUyRmFpX3RyYWNlJTJGZnJvbnRlbmQlMkZhcHAmcGFnZUV4dGVuc2lvbnM9dHN4JnBhZ2VFeHRlbnNpb25zPXRzJnBhZ2VFeHRlbnNpb25zPWpzeCZwYWdlRXh0ZW5zaW9ucz1qcyZyb290RGlyPSUyRlVzZXJzJTJGcnphcHAlMkZEb2N1bWVudHMlMkZBJTdCc3AlN0RBJTJGYWlfdHJhY2UlMkZmcm9udGVuZCZpc0Rldj10cnVlJnRzY29uZmlnUGF0aD10c2NvbmZpZy5qc29uJmJhc2VQYXRoPSZhc3NldFByZWZpeD0mbmV4dENvbmZpZ091dHB1dD0mcHJlZmVycmVkUmVnaW9uPSZtaWRkbGV3YXJlQ29uZmlnPWUzMCUzRCZpc0dsb2JhbE5vdEZvdW5kRW5hYmxlZD0hIiwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7O0FBQStGO0FBQ3ZDO0FBQ3FCO0FBQ3lDO0FBQ3RIO0FBQ0E7QUFDQTtBQUNBLHdCQUF3Qix5R0FBbUI7QUFDM0M7QUFDQSxjQUFjLGtFQUFTO0FBQ3ZCO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsS0FBSztBQUNMLGFBQWEsV0FBb0MsSUFBSSxDQUFFO0FBQ3ZELGdCQUFnQixNQUF1QztBQUN2RCxnREFBZ0QsR0FBRztBQUNuRDtBQUNBLFlBQVk7QUFDWixDQUFDO0FBQ0Q7QUFDQTtBQUNBO0FBQ0EsUUFBUSxzREFBc0Q7QUFDOUQ7QUFDQSxXQUFXLDRFQUFXO0FBQ3RCO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDMEY7O0FBRTFGIiwic291cmNlcyI6WyIiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgQXBwUm91dGVSb3V0ZU1vZHVsZSB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL3JvdXRlLW1vZHVsZXMvYXBwLXJvdXRlL21vZHVsZS5jb21waWxlZFwiO1xuaW1wb3J0IHsgUm91dGVLaW5kIH0gZnJvbSBcIm5leHQvZGlzdC9zZXJ2ZXIvcm91dGUta2luZFwiO1xuaW1wb3J0IHsgcGF0Y2hGZXRjaCBhcyBfcGF0Y2hGZXRjaCB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL2xpYi9wYXRjaC1mZXRjaFwiO1xuaW1wb3J0ICogYXMgdXNlcmxhbmQgZnJvbSBcIi9Vc2Vycy9yemFwcC9Eb2N1bWVudHMvQXtzcH1BL2FpX3RyYWNlL2Zyb250ZW5kL2FwcC9hcGkvaW52ZXN0aWdhdGlvbnMvWy4uLnBhdGhdL3JvdXRlLmpzXCI7XG4vLyBXZSBpbmplY3QgdGhlIG5leHRDb25maWdPdXRwdXQgaGVyZSBzbyB0aGF0IHdlIGNhbiB1c2UgdGhlbSBpbiB0aGUgcm91dGVcbi8vIG1vZHVsZS5cbmNvbnN0IG5leHRDb25maWdPdXRwdXQgPSBcIlwiXG5jb25zdCByb3V0ZU1vZHVsZSA9IG5ldyBBcHBSb3V0ZVJvdXRlTW9kdWxlKHtcbiAgICBkZWZpbml0aW9uOiB7XG4gICAgICAgIGtpbmQ6IFJvdXRlS2luZC5BUFBfUk9VVEUsXG4gICAgICAgIHBhZ2U6IFwiL2FwaS9pbnZlc3RpZ2F0aW9ucy9bLi4ucGF0aF0vcm91dGVcIixcbiAgICAgICAgcGF0aG5hbWU6IFwiL2FwaS9pbnZlc3RpZ2F0aW9ucy9bLi4ucGF0aF1cIixcbiAgICAgICAgZmlsZW5hbWU6IFwicm91dGVcIixcbiAgICAgICAgYnVuZGxlUGF0aDogXCJhcHAvYXBpL2ludmVzdGlnYXRpb25zL1suLi5wYXRoXS9yb3V0ZVwiXG4gICAgfSxcbiAgICBkaXN0RGlyOiBwcm9jZXNzLmVudi5fX05FWFRfUkVMQVRJVkVfRElTVF9ESVIgfHwgJycsXG4gICAgcHJvamVjdERpcjogcHJvY2Vzcy5lbnYuX19ORVhUX1JFTEFUSVZFX1BST0pFQ1RfRElSIHx8ICcnLFxuICAgIHJlc29sdmVkUGFnZVBhdGg6IFwiL1VzZXJzL3J6YXBwL0RvY3VtZW50cy9Be3NwfUEvYWlfdHJhY2UvZnJvbnRlbmQvYXBwL2FwaS9pbnZlc3RpZ2F0aW9ucy9bLi4ucGF0aF0vcm91dGUuanNcIixcbiAgICBuZXh0Q29uZmlnT3V0cHV0LFxuICAgIHVzZXJsYW5kXG59KTtcbi8vIFB1bGwgb3V0IHRoZSBleHBvcnRzIHRoYXQgd2UgbmVlZCB0byBleHBvc2UgZnJvbSB0aGUgbW9kdWxlLiBUaGlzIHNob3VsZFxuLy8gYmUgZWxpbWluYXRlZCB3aGVuIHdlJ3ZlIG1vdmVkIHRoZSBvdGhlciByb3V0ZXMgdG8gdGhlIG5ldyBmb3JtYXQuIFRoZXNlXG4vLyBhcmUgdXNlZCB0byBob29rIGludG8gdGhlIHJvdXRlLlxuY29uc3QgeyB3b3JrQXN5bmNTdG9yYWdlLCB3b3JrVW5pdEFzeW5jU3RvcmFnZSwgc2VydmVySG9va3MgfSA9IHJvdXRlTW9kdWxlO1xuZnVuY3Rpb24gcGF0Y2hGZXRjaCgpIHtcbiAgICByZXR1cm4gX3BhdGNoRmV0Y2goe1xuICAgICAgICB3b3JrQXN5bmNTdG9yYWdlLFxuICAgICAgICB3b3JrVW5pdEFzeW5jU3RvcmFnZVxuICAgIH0pO1xufVxuZXhwb3J0IHsgcm91dGVNb2R1bGUsIHdvcmtBc3luY1N0b3JhZ2UsIHdvcmtVbml0QXN5bmNTdG9yYWdlLCBzZXJ2ZXJIb29rcywgcGF0Y2hGZXRjaCwgIH07XG5cbi8vIyBzb3VyY2VNYXBwaW5nVVJMPWFwcC1yb3V0ZS5qcy5tYXAiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&page=%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute.js&appDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=!\n");

/***/ }),

/***/ "(rsc)/./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true!":
/*!******************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true! ***!
  \******************************************************************************************************/
/***/ (() => {



/***/ }),

/***/ "(ssr)/./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true!":
/*!******************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-flight-client-entry-loader.js?server=true! ***!
  \******************************************************************************************************/
/***/ (() => {



/***/ }),

/***/ "../app-render/work-async-storage.external":
/*!*****************************************************************************!*\
  !*** external "next/dist/server/app-render/work-async-storage.external.js" ***!
  \*****************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/server/app-render/work-async-storage.external.js");

/***/ }),

/***/ "./work-unit-async-storage.external":
/*!**********************************************************************************!*\
  !*** external "next/dist/server/app-render/work-unit-async-storage.external.js" ***!
  \**********************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/server/app-render/work-unit-async-storage.external.js");

/***/ }),

/***/ "next/dist/compiled/next-server/app-page.runtime.dev.js":
/*!*************************************************************************!*\
  !*** external "next/dist/compiled/next-server/app-page.runtime.dev.js" ***!
  \*************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/compiled/next-server/app-page.runtime.dev.js");

/***/ }),

/***/ "next/dist/compiled/next-server/app-route.runtime.dev.js":
/*!**************************************************************************!*\
  !*** external "next/dist/compiled/next-server/app-route.runtime.dev.js" ***!
  \**************************************************************************/
/***/ ((module) => {

"use strict";
module.exports = require("next/dist/compiled/next-server/app-route.runtime.dev.js");

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../../../../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/next"], () => (__webpack_exec__("(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&page=%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2F%5B...path%5D%2Froute.js&appDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2FUsers%2Frzapp%2FDocuments%2FA%7Bsp%7DA%2Fai_trace%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=!")));
module.exports = __webpack_exports__;

})();