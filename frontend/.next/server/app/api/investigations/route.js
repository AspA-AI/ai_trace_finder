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
exports.id = "app/api/investigations/route";
exports.ids = ["app/api/investigations/route"];
exports.modules = {

/***/ "(rsc)/./app/api/investigations/route.js":
/*!*****************************************!*\
  !*** ./app/api/investigations/route.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   GET: () => (/* binding */ GET),\n/* harmony export */   POST: () => (/* binding */ POST)\n/* harmony export */ });\n/* harmony import */ var _lib_backend__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../../lib/backend */ \"(rsc)/./lib/backend.js\");\n\nasync function POST(request) {\n    return (0,_lib_backend__WEBPACK_IMPORTED_MODULE_0__.proxyRequest)(request, \"/investigations\");\n}\nasync function GET(request) {\n    return (0,_lib_backend__WEBPACK_IMPORTED_MODULE_0__.proxyRequest)(request, \"/investigations\");\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9hcHAvYXBpL2ludmVzdGlnYXRpb25zL3JvdXRlLmpzIiwibWFwcGluZ3MiOiI7Ozs7OztBQUFvRDtBQUU3QyxlQUFlQyxLQUFLQyxPQUFPO0lBQ2hDLE9BQU9GLDBEQUFZQSxDQUFDRSxTQUFTO0FBQy9CO0FBRU8sZUFBZUMsSUFBSUQsT0FBTztJQUMvQixPQUFPRiwwREFBWUEsQ0FBQ0UsU0FBUztBQUMvQiIsInNvdXJjZXMiOlsiL3ZlcmNlbC9zaGFyZS92MC1wcm9qZWN0L2Zyb250ZW5kL2FwcC9hcGkvaW52ZXN0aWdhdGlvbnMvcm91dGUuanMiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgcHJveHlSZXF1ZXN0IH0gZnJvbSBcIi4uLy4uLy4uL2xpYi9iYWNrZW5kXCI7XG5cbmV4cG9ydCBhc3luYyBmdW5jdGlvbiBQT1NUKHJlcXVlc3QpIHtcbiAgcmV0dXJuIHByb3h5UmVxdWVzdChyZXF1ZXN0LCBcIi9pbnZlc3RpZ2F0aW9uc1wiKTtcbn1cblxuZXhwb3J0IGFzeW5jIGZ1bmN0aW9uIEdFVChyZXF1ZXN0KSB7XG4gIHJldHVybiBwcm94eVJlcXVlc3QocmVxdWVzdCwgXCIvaW52ZXN0aWdhdGlvbnNcIik7XG59XG4iXSwibmFtZXMiOlsicHJveHlSZXF1ZXN0IiwiUE9TVCIsInJlcXVlc3QiLCJHRVQiXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///(rsc)/./app/api/investigations/route.js\n");

/***/ }),

/***/ "(rsc)/./lib/backend.js":
/*!************************!*\
  !*** ./lib/backend.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   proxyRequest: () => (/* binding */ proxyRequest)\n/* harmony export */ });\nconst BACKEND_URL = process.env.BACKEND_URL || \"http://127.0.0.1:8000\";\nasync function proxyRequest(request, path) {\n    const incoming = new URL(request.url);\n    const url = `${BACKEND_URL}${path}${incoming.search}`;\n    const hasBody = ![\n        \"GET\",\n        \"HEAD\"\n    ].includes(request.method);\n    const upstream = await fetch(url, {\n        method: request.method,\n        headers: filterHeaders(request.headers),\n        body: hasBody ? await request.arrayBuffer() : undefined,\n        duplex: hasBody ? \"half\" : undefined\n    });\n    return new Response(upstream.body, {\n        status: upstream.status,\n        headers: filterResponseHeaders(upstream.headers)\n    });\n}\nfunction filterHeaders(headers) {\n    const out = new Headers();\n    for (const [key, value] of headers.entries()){\n        if ([\n            \"host\",\n            \"connection\",\n            \"content-length\"\n        ].includes(key.toLowerCase())) continue;\n        out.set(key, value);\n    }\n    return out;\n}\nfunction filterResponseHeaders(headers) {\n    const out = new Headers();\n    for (const [key, value] of headers.entries()){\n        if ([\n            \"transfer-encoding\",\n            \"connection\",\n            \"content-length\"\n        ].includes(key.toLowerCase())) continue;\n        out.set(key, value);\n    }\n    return out;\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9saWIvYmFja2VuZC5qcyIsIm1hcHBpbmdzIjoiOzs7O0FBQUEsTUFBTUEsY0FBY0MsUUFBUUMsR0FBRyxDQUFDRixXQUFXLElBQUk7QUFFeEMsZUFBZUcsYUFBYUMsT0FBTyxFQUFFQyxJQUFJO0lBQzlDLE1BQU1DLFdBQVcsSUFBSUMsSUFBSUgsUUFBUUksR0FBRztJQUNwQyxNQUFNQSxNQUFNLEdBQUdSLGNBQWNLLE9BQU9DLFNBQVNHLE1BQU0sRUFBRTtJQUNyRCxNQUFNQyxVQUFVLENBQUM7UUFBQztRQUFPO0tBQU8sQ0FBQ0MsUUFBUSxDQUFDUCxRQUFRUSxNQUFNO0lBQ3hELE1BQU1DLFdBQVcsTUFBTUMsTUFBTU4sS0FBSztRQUNoQ0ksUUFBUVIsUUFBUVEsTUFBTTtRQUN0QkcsU0FBU0MsY0FBY1osUUFBUVcsT0FBTztRQUN0Q0UsTUFBTVAsVUFBVSxNQUFNTixRQUFRYyxXQUFXLEtBQUtDO1FBQzlDQyxRQUFRVixVQUFVLFNBQVNTO0lBQzdCO0lBQ0EsT0FBTyxJQUFJRSxTQUFTUixTQUFTSSxJQUFJLEVBQUU7UUFDakNLLFFBQVFULFNBQVNTLE1BQU07UUFDdkJQLFNBQVNRLHNCQUFzQlYsU0FBU0UsT0FBTztJQUNqRDtBQUNGO0FBRUEsU0FBU0MsY0FBY0QsT0FBTztJQUM1QixNQUFNUyxNQUFNLElBQUlDO0lBQ2hCLEtBQUssTUFBTSxDQUFDQyxLQUFLQyxNQUFNLElBQUlaLFFBQVFhLE9BQU8sR0FBSTtRQUM1QyxJQUFJO1lBQUM7WUFBUTtZQUFjO1NBQWlCLENBQUNqQixRQUFRLENBQUNlLElBQUlHLFdBQVcsS0FBSztRQUMxRUwsSUFBSU0sR0FBRyxDQUFDSixLQUFLQztJQUNmO0lBQ0EsT0FBT0g7QUFDVDtBQUVBLFNBQVNELHNCQUFzQlIsT0FBTztJQUNwQyxNQUFNUyxNQUFNLElBQUlDO0lBQ2hCLEtBQUssTUFBTSxDQUFDQyxLQUFLQyxNQUFNLElBQUlaLFFBQVFhLE9BQU8sR0FBSTtRQUM1QyxJQUFJO1lBQUM7WUFBcUI7WUFBYztTQUFpQixDQUFDakIsUUFBUSxDQUFDZSxJQUFJRyxXQUFXLEtBQUs7UUFDdkZMLElBQUlNLEdBQUcsQ0FBQ0osS0FBS0M7SUFDZjtJQUNBLE9BQU9IO0FBQ1QiLCJzb3VyY2VzIjpbIi92ZXJjZWwvc2hhcmUvdjAtcHJvamVjdC9mcm9udGVuZC9saWIvYmFja2VuZC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJjb25zdCBCQUNLRU5EX1VSTCA9IHByb2Nlc3MuZW52LkJBQ0tFTkRfVVJMIHx8IFwiaHR0cDovLzEyNy4wLjAuMTo4MDAwXCI7XG5cbmV4cG9ydCBhc3luYyBmdW5jdGlvbiBwcm94eVJlcXVlc3QocmVxdWVzdCwgcGF0aCkge1xuICBjb25zdCBpbmNvbWluZyA9IG5ldyBVUkwocmVxdWVzdC51cmwpO1xuICBjb25zdCB1cmwgPSBgJHtCQUNLRU5EX1VSTH0ke3BhdGh9JHtpbmNvbWluZy5zZWFyY2h9YDtcbiAgY29uc3QgaGFzQm9keSA9ICFbXCJHRVRcIiwgXCJIRUFEXCJdLmluY2x1ZGVzKHJlcXVlc3QubWV0aG9kKTtcbiAgY29uc3QgdXBzdHJlYW0gPSBhd2FpdCBmZXRjaCh1cmwsIHtcbiAgICBtZXRob2Q6IHJlcXVlc3QubWV0aG9kLFxuICAgIGhlYWRlcnM6IGZpbHRlckhlYWRlcnMocmVxdWVzdC5oZWFkZXJzKSxcbiAgICBib2R5OiBoYXNCb2R5ID8gYXdhaXQgcmVxdWVzdC5hcnJheUJ1ZmZlcigpIDogdW5kZWZpbmVkLFxuICAgIGR1cGxleDogaGFzQm9keSA/IFwiaGFsZlwiIDogdW5kZWZpbmVkLFxuICB9KTtcbiAgcmV0dXJuIG5ldyBSZXNwb25zZSh1cHN0cmVhbS5ib2R5LCB7XG4gICAgc3RhdHVzOiB1cHN0cmVhbS5zdGF0dXMsXG4gICAgaGVhZGVyczogZmlsdGVyUmVzcG9uc2VIZWFkZXJzKHVwc3RyZWFtLmhlYWRlcnMpLFxuICB9KTtcbn1cblxuZnVuY3Rpb24gZmlsdGVySGVhZGVycyhoZWFkZXJzKSB7XG4gIGNvbnN0IG91dCA9IG5ldyBIZWFkZXJzKCk7XG4gIGZvciAoY29uc3QgW2tleSwgdmFsdWVdIG9mIGhlYWRlcnMuZW50cmllcygpKSB7XG4gICAgaWYgKFtcImhvc3RcIiwgXCJjb25uZWN0aW9uXCIsIFwiY29udGVudC1sZW5ndGhcIl0uaW5jbHVkZXMoa2V5LnRvTG93ZXJDYXNlKCkpKSBjb250aW51ZTtcbiAgICBvdXQuc2V0KGtleSwgdmFsdWUpO1xuICB9XG4gIHJldHVybiBvdXQ7XG59XG5cbmZ1bmN0aW9uIGZpbHRlclJlc3BvbnNlSGVhZGVycyhoZWFkZXJzKSB7XG4gIGNvbnN0IG91dCA9IG5ldyBIZWFkZXJzKCk7XG4gIGZvciAoY29uc3QgW2tleSwgdmFsdWVdIG9mIGhlYWRlcnMuZW50cmllcygpKSB7XG4gICAgaWYgKFtcInRyYW5zZmVyLWVuY29kaW5nXCIsIFwiY29ubmVjdGlvblwiLCBcImNvbnRlbnQtbGVuZ3RoXCJdLmluY2x1ZGVzKGtleS50b0xvd2VyQ2FzZSgpKSkgY29udGludWU7XG4gICAgb3V0LnNldChrZXksIHZhbHVlKTtcbiAgfVxuICByZXR1cm4gb3V0O1xufVxuIl0sIm5hbWVzIjpbIkJBQ0tFTkRfVVJMIiwicHJvY2VzcyIsImVudiIsInByb3h5UmVxdWVzdCIsInJlcXVlc3QiLCJwYXRoIiwiaW5jb21pbmciLCJVUkwiLCJ1cmwiLCJzZWFyY2giLCJoYXNCb2R5IiwiaW5jbHVkZXMiLCJtZXRob2QiLCJ1cHN0cmVhbSIsImZldGNoIiwiaGVhZGVycyIsImZpbHRlckhlYWRlcnMiLCJib2R5IiwiYXJyYXlCdWZmZXIiLCJ1bmRlZmluZWQiLCJkdXBsZXgiLCJSZXNwb25zZSIsInN0YXR1cyIsImZpbHRlclJlc3BvbnNlSGVhZGVycyIsIm91dCIsIkhlYWRlcnMiLCJrZXkiLCJ2YWx1ZSIsImVudHJpZXMiLCJ0b0xvd2VyQ2FzZSIsInNldCJdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///(rsc)/./lib/backend.js\n");

/***/ }),

/***/ "(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2Froute&page=%2Fapi%2Finvestigations%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2Froute.js&appDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=!":
/*!***************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2Froute&page=%2Fapi%2Finvestigations%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2Froute.js&appDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=! ***!
  \***************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   patchFetch: () => (/* binding */ patchFetch),\n/* harmony export */   routeModule: () => (/* binding */ routeModule),\n/* harmony export */   serverHooks: () => (/* binding */ serverHooks),\n/* harmony export */   workAsyncStorage: () => (/* binding */ workAsyncStorage),\n/* harmony export */   workUnitAsyncStorage: () => (/* binding */ workUnitAsyncStorage)\n/* harmony export */ });\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next/dist/server/route-modules/app-route/module.compiled */ \"(rsc)/./node_modules/next/dist/server/route-modules/app-route/module.compiled.js\");\n/* harmony import */ var next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! next/dist/server/route-kind */ \"(rsc)/./node_modules/next/dist/server/route-kind.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! next/dist/server/lib/patch-fetch */ \"(rsc)/./node_modules/next/dist/server/lib/patch-fetch.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var _vercel_share_v0_project_frontend_app_api_investigations_route_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./app/api/investigations/route.js */ \"(rsc)/./app/api/investigations/route.js\");\n\n\n\n\n// We inject the nextConfigOutput here so that we can use them in the route\n// module.\nconst nextConfigOutput = \"\"\nconst routeModule = new next_dist_server_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__.AppRouteRouteModule({\n    definition: {\n        kind: next_dist_server_route_kind__WEBPACK_IMPORTED_MODULE_1__.RouteKind.APP_ROUTE,\n        page: \"/api/investigations/route\",\n        pathname: \"/api/investigations\",\n        filename: \"route\",\n        bundlePath: \"app/api/investigations/route\"\n    },\n    distDir: \".next\" || 0,\n    projectDir:  false || '',\n    resolvedPagePath: \"/vercel/share/v0-project/frontend/app/api/investigations/route.js\",\n    nextConfigOutput,\n    userland: _vercel_share_v0_project_frontend_app_api_investigations_route_js__WEBPACK_IMPORTED_MODULE_3__\n});\n// Pull out the exports that we need to expose from the module. This should\n// be eliminated when we've moved the other routes to the new format. These\n// are used to hook into the route.\nconst { workAsyncStorage, workUnitAsyncStorage, serverHooks } = routeModule;\nfunction patchFetch() {\n    return (0,next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__.patchFetch)({\n        workAsyncStorage,\n        workUnitAsyncStorage\n    });\n}\n\n\n//# sourceMappingURL=app-route.js.map//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9ub2RlX21vZHVsZXMvbmV4dC9kaXN0L2J1aWxkL3dlYnBhY2svbG9hZGVycy9uZXh0LWFwcC1sb2FkZXIvaW5kZXguanM/bmFtZT1hcHAlMkZhcGklMkZpbnZlc3RpZ2F0aW9ucyUyRnJvdXRlJnBhZ2U9JTJGYXBpJTJGaW52ZXN0aWdhdGlvbnMlMkZyb3V0ZSZhcHBQYXRocz0mcGFnZVBhdGg9cHJpdmF0ZS1uZXh0LWFwcC1kaXIlMkZhcGklMkZpbnZlc3RpZ2F0aW9ucyUyRnJvdXRlLmpzJmFwcERpcj0lMkZ2ZXJjZWwlMkZzaGFyZSUyRnYwLXByb2plY3QlMkZmcm9udGVuZCUyRmFwcCZwYWdlRXh0ZW5zaW9ucz10c3gmcGFnZUV4dGVuc2lvbnM9dHMmcGFnZUV4dGVuc2lvbnM9anN4JnBhZ2VFeHRlbnNpb25zPWpzJnJvb3REaXI9JTJGdmVyY2VsJTJGc2hhcmUlMkZ2MC1wcm9qZWN0JTJGZnJvbnRlbmQmaXNEZXY9dHJ1ZSZ0c2NvbmZpZ1BhdGg9dHNjb25maWcuanNvbiZiYXNlUGF0aD0mYXNzZXRQcmVmaXg9Jm5leHRDb25maWdPdXRwdXQ9JnByZWZlcnJlZFJlZ2lvbj0mbWlkZGxld2FyZUNvbmZpZz1lMzAlM0QmaXNHbG9iYWxOb3RGb3VuZEVuYWJsZWQ9ISIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7OztBQUErRjtBQUN2QztBQUNxQjtBQUNpQjtBQUM5RjtBQUNBO0FBQ0E7QUFDQSx3QkFBd0IseUdBQW1CO0FBQzNDO0FBQ0EsY0FBYyxrRUFBUztBQUN2QjtBQUNBO0FBQ0E7QUFDQTtBQUNBLEtBQUs7QUFDTCxhQUFhLE9BQW9DLElBQUksQ0FBRTtBQUN2RCxnQkFBZ0IsTUFBdUM7QUFDdkQ7QUFDQTtBQUNBLFlBQVk7QUFDWixDQUFDO0FBQ0Q7QUFDQTtBQUNBO0FBQ0EsUUFBUSxzREFBc0Q7QUFDOUQ7QUFDQSxXQUFXLDRFQUFXO0FBQ3RCO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDMEY7O0FBRTFGIiwic291cmNlcyI6WyIiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgQXBwUm91dGVSb3V0ZU1vZHVsZSB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL3JvdXRlLW1vZHVsZXMvYXBwLXJvdXRlL21vZHVsZS5jb21waWxlZFwiO1xuaW1wb3J0IHsgUm91dGVLaW5kIH0gZnJvbSBcIm5leHQvZGlzdC9zZXJ2ZXIvcm91dGUta2luZFwiO1xuaW1wb3J0IHsgcGF0Y2hGZXRjaCBhcyBfcGF0Y2hGZXRjaCB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL2xpYi9wYXRjaC1mZXRjaFwiO1xuaW1wb3J0ICogYXMgdXNlcmxhbmQgZnJvbSBcIi92ZXJjZWwvc2hhcmUvdjAtcHJvamVjdC9mcm9udGVuZC9hcHAvYXBpL2ludmVzdGlnYXRpb25zL3JvdXRlLmpzXCI7XG4vLyBXZSBpbmplY3QgdGhlIG5leHRDb25maWdPdXRwdXQgaGVyZSBzbyB0aGF0IHdlIGNhbiB1c2UgdGhlbSBpbiB0aGUgcm91dGVcbi8vIG1vZHVsZS5cbmNvbnN0IG5leHRDb25maWdPdXRwdXQgPSBcIlwiXG5jb25zdCByb3V0ZU1vZHVsZSA9IG5ldyBBcHBSb3V0ZVJvdXRlTW9kdWxlKHtcbiAgICBkZWZpbml0aW9uOiB7XG4gICAgICAgIGtpbmQ6IFJvdXRlS2luZC5BUFBfUk9VVEUsXG4gICAgICAgIHBhZ2U6IFwiL2FwaS9pbnZlc3RpZ2F0aW9ucy9yb3V0ZVwiLFxuICAgICAgICBwYXRobmFtZTogXCIvYXBpL2ludmVzdGlnYXRpb25zXCIsXG4gICAgICAgIGZpbGVuYW1lOiBcInJvdXRlXCIsXG4gICAgICAgIGJ1bmRsZVBhdGg6IFwiYXBwL2FwaS9pbnZlc3RpZ2F0aW9ucy9yb3V0ZVwiXG4gICAgfSxcbiAgICBkaXN0RGlyOiBwcm9jZXNzLmVudi5fX05FWFRfUkVMQVRJVkVfRElTVF9ESVIgfHwgJycsXG4gICAgcHJvamVjdERpcjogcHJvY2Vzcy5lbnYuX19ORVhUX1JFTEFUSVZFX1BST0pFQ1RfRElSIHx8ICcnLFxuICAgIHJlc29sdmVkUGFnZVBhdGg6IFwiL3ZlcmNlbC9zaGFyZS92MC1wcm9qZWN0L2Zyb250ZW5kL2FwcC9hcGkvaW52ZXN0aWdhdGlvbnMvcm91dGUuanNcIixcbiAgICBuZXh0Q29uZmlnT3V0cHV0LFxuICAgIHVzZXJsYW5kXG59KTtcbi8vIFB1bGwgb3V0IHRoZSBleHBvcnRzIHRoYXQgd2UgbmVlZCB0byBleHBvc2UgZnJvbSB0aGUgbW9kdWxlLiBUaGlzIHNob3VsZFxuLy8gYmUgZWxpbWluYXRlZCB3aGVuIHdlJ3ZlIG1vdmVkIHRoZSBvdGhlciByb3V0ZXMgdG8gdGhlIG5ldyBmb3JtYXQuIFRoZXNlXG4vLyBhcmUgdXNlZCB0byBob29rIGludG8gdGhlIHJvdXRlLlxuY29uc3QgeyB3b3JrQXN5bmNTdG9yYWdlLCB3b3JrVW5pdEFzeW5jU3RvcmFnZSwgc2VydmVySG9va3MgfSA9IHJvdXRlTW9kdWxlO1xuZnVuY3Rpb24gcGF0Y2hGZXRjaCgpIHtcbiAgICByZXR1cm4gX3BhdGNoRmV0Y2goe1xuICAgICAgICB3b3JrQXN5bmNTdG9yYWdlLFxuICAgICAgICB3b3JrVW5pdEFzeW5jU3RvcmFnZVxuICAgIH0pO1xufVxuZXhwb3J0IHsgcm91dGVNb2R1bGUsIHdvcmtBc3luY1N0b3JhZ2UsIHdvcmtVbml0QXN5bmNTdG9yYWdlLCBzZXJ2ZXJIb29rcywgcGF0Y2hGZXRjaCwgIH07XG5cbi8vIyBzb3VyY2VNYXBwaW5nVVJMPWFwcC1yb3V0ZS5qcy5tYXAiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2Froute&page=%2Fapi%2Finvestigations%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2Froute.js&appDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=!\n");

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
var __webpack_require__ = require("../../../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/next"], () => (__webpack_exec__("(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.js?name=app%2Fapi%2Finvestigations%2Froute&page=%2Fapi%2Finvestigations%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Finvestigations%2Froute.js&appDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend%2Fapp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=%2Fvercel%2Fshare%2Fv0-project%2Ffrontend&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=&preferredRegion=&middlewareConfig=e30%3D&isGlobalNotFoundEnabled=!")));
module.exports = __webpack_exports__;

})();