package com.landsense.ai.di

import android.content.Context
import androidx.room.Room
import com.landsense.ai.data.local.AppDatabase
import com.landsense.ai.data.local.ObservationDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "landsense_db"
        ).build()
    }

    @Provides
    @Singleton
    fun provideObservationDao(database: AppDatabase): ObservationDao {
        return database.observationDao()
    }
}
