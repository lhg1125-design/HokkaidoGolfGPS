plugins { id("com.android.application") }

android {
    namespace = "com.hokkaidogolf.trip"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.hokkaidogolf.trip"
        minSdk = 26
        targetSdk = 35
        versionCode = 47
        versionName = "1.12.4-hole-step-buttons"
    }

    buildTypes {
        release { isMinifyEnabled = false }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
