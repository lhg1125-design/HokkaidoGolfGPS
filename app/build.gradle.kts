plugins { id("com.android.application") }

android {
    namespace = "com.hokkaidogolf.trip"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.hokkaidogolf.trip"
        minSdk = 26
        targetSdk = 35
        versionCode = 14
        versionName = "1.2.1-artwork-fidelity"
    }

    buildTypes {
        release { isMinifyEnabled = false }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
