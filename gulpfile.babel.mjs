/* Theme builder and previewer.

   Minimize JavaScript.
   Convert SASS to CSS and minify.
*/
import Promise from "promise"
import yargs from "yargs"
import {hideBin} from "yargs/helpers"
import gulp from "gulp"
import gulpSass from "gulp-sass"
import * as sassCompiler from "sass"
import postcss from "gulp-postcss"
import scssModule from "postcss-scss"
const scss = (scssModule && scssModule.default) ? scssModule.default : scssModule
import sortCssMq from 'postcss-sort-media-queries'
import autoprefixer from "autoprefixer"
import gulpif from "gulp-if"
import concat from "gulp-concat"
import terser from '@rollup/plugin-terser'
import {rollup} from "rollup"
import {babel as rollupBabel, getBabelOutputPlugin} from "@rollup/plugin-babel"
import gStylelintEsm from 'gulp-stylelint-esm'
import eslint from "gulp-eslint"
import rev from "gulp-rev"
import revReplace from "gulp-rev-replace"
import vinylPaths from "vinyl-paths"
import {deleteAsync, deleteSync} from "del"
import path from "path"
import inlineSvg from "postcss-inline-svg"
import cssSvgo from "postcss-svgo"
import replace from "gulp-replace"
import outputManifest from "rollup-plugin-output-manifest"
import sourcemaps from "gulp-sourcemaps"

const sass = gulpSass(sassCompiler)

/* Argument Flags */
const args = yargs(hideBin(process.argv))
  .boolean("compress")
  .boolean("lint")
  .boolean("clean")
  .boolean("sourcemaps")
  .boolean("buildzensical")
  .boolean("revision")
  .default("zensical", "zensical")
  .argv

// ------------------------------
// Configuration
// ------------------------------
const config = {
  files: {
    scss: "./docs/src/scss/**/*.scss",
    css: [
      "./docs/theme/assets/pymdownx-extras/*.css",
      "./docs/theme/assets/pymdownx-extras/*.css.map"
    ],
    jsSrc: "./docs/src/js/**/*.js",
    js: [
      "./docs/theme/assets/pymdownx-extras/*.js",
      "./docs/theme/assets/pymdownx-extras/*.js.map"
    ],
    gulp: "gulpfile.babel.mjs",
    zensicalSrc: "./docs/src/zensical.yml"
  },
  folders: {
    zensical: "./site",
    theme: "./docs/theme/assets/pymdownx-extras",
    src: "./docs/src"
  },
  compress: {
    enabled: args.compress,
    jsOptions: {
      conditionals: true,
      unused: true,
      comparisons: true,
      sequences: true,
      dead_code: true,    // eslint-disable-line camelcase
      evaluate: true,
      if_return: true,    // eslint-disable-line camelcase
      join_vars: true     // eslint-disable-line camelcase,
    }
  },
  lint: {
    enabled: args.lint
  },
  clean: args.clean,
  sourcemaps: args.sourcemaps,
  revision: args.revision
}

const rollupjs = async(sources, options) => {

  const pluginModules = [rollupBabel({babelHelpers: "bundled"})]
  if (options.revision) {
    pluginModules.push(outputManifest.default({fileName: "manifest-js.json", isMerge: options.merge}))
  }
