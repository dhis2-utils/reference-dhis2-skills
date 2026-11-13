package org.example.householdlisting.data

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.withContext
import org.hisp.dhis.android.core.D2
import org.hisp.dhis.android.core.enrollment.EnrollmentCreateProjection
import org.hisp.dhis.android.core.trackedentity.TrackedEntityInstanceCreateProjection
import java.util.Date
import java.util.concurrent.Executors

// One thread for all SDK work so writes never race each other.
private val sdkDispatcher = Executors.newSingleThreadExecutor().asCoroutineDispatcher()

class HouseholdWriter(private val d2: D2) {

    // The Household program has one stage, "Visit", with autoGenerateEvent = true,
    // so the SDK creates the first visit when we enroll.
    suspend fun registerHousehold(
        orgUnit: String, tet: String, program: String,
        attributes: Map<String, String>,   // includes "members" (INTEGER) typed by the user
    ): String = withContext(sdkDispatcher) {
        val teis = d2.trackedEntityModule().trackedEntityInstances()
        val tei = teis.blockingAdd(TrackedEntityInstanceCreateProjection.create(orgUnit, tet))
        attributes.forEach { (attr, value) ->
            // blockingSet throws if the value doesn't match the attribute's value type
            d2.trackedEntityModule().trackedEntityAttributeValues().value(attr, tei).blockingSet(value)
        }
        val enrollments = d2.enrollmentModule().enrollments()
        val enr = enrollments.blockingAdd(EnrollmentCreateProjection.create(orgUnit, program, tei))
        enrollments.uid(enr).setEnrollmentDate(Date())
        enrollments.uid(enr).setIncidentDate(Date())
        tei
    }

    // Called from a "Send" button: push everything that is pending.
    suspend fun sendAll() = withContext(sdkDispatcher) {
        d2.trackedEntityModule().trackedEntityInstances().blockingUpload()
    }

    // Called by a periodic WorkManager worker every 15 minutes.
    suspend fun refreshMetadata() = withContext(sdkDispatcher) {
        d2.metadataModule().blockingDownload()
    }
}
