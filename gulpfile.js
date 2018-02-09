const gulp = require('gulp');
const sourcemaps = require('gulp-sourcemaps');
const source = require('vinyl-source-stream');
const buffer = require('vinyl-buffer');
const browserify = require('browserify');
const concat = require('gulp-concat');
const watchify = require('watchify');
const babel = require('babelify');
const sass = require('gulp-sass');
const prefix = require('gulp-autoprefixer');
// const browserSync = require('browser-sync').create();

function compile(watch) {
  let bundler = watchify(browserify('./src/js/index.jsx', { debug: true, extensions: ['.js', '.jsx']}).transform(babel, {presets: ["es2015", 'react']}));

  function rebundle() {
    bundler.bundle()
      .on('error', function(err) { console.error(err); this.emit('end'); })
      .pipe(source('index.js'))
      .pipe(buffer())
      .pipe(sourcemaps.init({ loadMaps: true }))
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./static/js'));
  }

  if (watch) {
    bundler.on('update', function() {
      console.log('-> bundling...' + new Date());
      rebundle();
    });
  }

  rebundle();
}

function watch() {
  return compile(true);
}

gulp.task('dev-sass', function() { // Compile and concat SCSS
  gulp.src('./src/scss/app.scss')
    .pipe(sourcemaps.init())
    .pipe(sass().on('error', sass.logError))
    .pipe(prefix())
    .pipe(sourcemaps.write())
    .pipe(gulp.dest('./static/css'));
});

gulp.task('watch-sass', function() { // Watch specified directories for changes.
  gulp.watch('./src/**/*.scss', ['dev-sass']);
});

gulp.task('build', function() { return compile(); });
gulp.task('watch', function() { return watch(); });

gulp.task('default', ['watch-sass', 'watch']);

