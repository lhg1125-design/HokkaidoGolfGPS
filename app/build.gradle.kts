plugins { id("com.android.application") }

android {
    namespace = "com.hokkaidogolf.trip"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.hokkaidogolf.trip"
        minSdk = 26
        targetSdk = 35
        versionCode = 26
        versionName = "1.8.0-premium-course-art"
    }

    buildTypes {
        release { isMinifyEnabled = false }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
