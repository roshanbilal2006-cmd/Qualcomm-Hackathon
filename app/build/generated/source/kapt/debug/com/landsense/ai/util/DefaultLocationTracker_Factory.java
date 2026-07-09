package com.landsense.ai.util;

import android.content.Context;
import com.google.android.gms.location.FusedLocationProviderClient;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata("dagger.hilt.android.qualifiers.ApplicationContext")
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava",
    "cast"
})
public final class DefaultLocationTracker_Factory implements Factory<DefaultLocationTracker> {
  private final Provider<FusedLocationProviderClient> fusedLocationProviderClientProvider;

  private final Provider<Context> contextProvider;

  public DefaultLocationTracker_Factory(
      Provider<FusedLocationProviderClient> fusedLocationProviderClientProvider,
      Provider<Context> contextProvider) {
    this.fusedLocationProviderClientProvider = fusedLocationProviderClientProvider;
    this.contextProvider = contextProvider;
  }

  @Override
  public DefaultLocationTracker get() {
    return newInstance(fusedLocationProviderClientProvider.get(), contextProvider.get());
  }

  public static DefaultLocationTracker_Factory create(
      Provider<FusedLocationProviderClient> fusedLocationProviderClientProvider,
      Provider<Context> contextProvider) {
    return new DefaultLocationTracker_Factory(fusedLocationProviderClientProvider, contextProvider);
  }

  public static DefaultLocationTracker newInstance(
      FusedLocationProviderClient fusedLocationProviderClient, Context context) {
    return new DefaultLocationTracker(fusedLocationProviderClient, context);
  }
}
