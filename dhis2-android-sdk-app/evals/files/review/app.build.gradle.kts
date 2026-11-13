plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "org.example.householdlisting"
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig {
        applicationId = "org.example.householdlisting"
        minSdk = libs.versions.minSdk.get().toInt()
        targetSdk = 36
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation(libs.dhis2.android.sdk)
    implementation(libs.dhis2.rule.engine)
    implementation(platform(libs.compose.bom))
    implementation(libs.coroutines.android)
}
