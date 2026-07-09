package com.landsense.ai.di;

import android.content.Context;
import com.google.android.gms.location.FusedLocationProviderClient;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
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
public final class LocationModule_Companion_ProvideFusedLocationProviderClientFactory implements Factory<FusedLocationProviderClient> {
  private final Provider<Context> contextProvider;

  public LocationModule_Companion_ProvideFusedLocationProviderClientFactory(
      Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public FusedLocationProviderClient get() {
    return provideFusedLocationProviderClient(contextProvider.get());
  }

  public static LocationModule_Companion_ProvideFusedLocationProviderClientFactory create(
      Provider<Context> contextProvider) {
    return new LocationModule_Companion_ProvideFusedLocationProviderClientFactory(contextProvider);
  }

  public static FusedLocationProviderClient provideFusedLocationProviderClient(Context context) {
    return Preconditions.checkNotNullFromProvides(LocationModule.Companion.provideFusedLocationProviderClient(context));
  }
}
