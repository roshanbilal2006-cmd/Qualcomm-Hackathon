package com.landsense.ai.util;

@javax.inject.Singleton()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u0019\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0001\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0002\u0010\u0006J\u0010\u0010\u0007\u001a\u0004\u0018\u00010\bH\u0097@\u00a2\u0006\u0002\u0010\tR\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\n"}, d2 = {"Lcom/landsense/ai/util/DefaultLocationTracker;", "Lcom/landsense/ai/util/LocationTracker;", "fusedLocationProviderClient", "Lcom/google/android/gms/location/FusedLocationProviderClient;", "context", "Landroid/content/Context;", "(Lcom/google/android/gms/location/FusedLocationProviderClient;Landroid/content/Context;)V", "getCurrentLocation", "Landroid/location/Location;", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public final class DefaultLocationTracker implements com.landsense.ai.util.LocationTracker {
    @org.jetbrains.annotations.NotNull()
    private final com.google.android.gms.location.FusedLocationProviderClient fusedLocationProviderClient = null;
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    
    @javax.inject.Inject()
    public DefaultLocationTracker(@org.jetbrains.annotations.NotNull()
    com.google.android.gms.location.FusedLocationProviderClient fusedLocationProviderClient, @dagger.hilt.android.qualifiers.ApplicationContext()
    @org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super();
    }
    
    @java.lang.Override()
    @android.annotation.SuppressLint(value = {"MissingPermission"})
    @org.jetbrains.annotations.Nullable()
    public java.lang.Object getCurrentLocation(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super android.location.Location> $completion) {
        return null;
    }
}