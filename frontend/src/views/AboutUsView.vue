<template>
  <div>
    <Navbar />
    
    <!-- About Us Content -->
    <main class="min-h-screen bg-brand-pink-lighter pt-20 pb-16">
      <!-- First Section -->
      <section class="container mx-auto px-4 py-16">
        <div class="main-grid">
          <!-- Text Content -->
          <div class="space-y-8">
            <!-- Brand Name -->
            <h3 class="font-comfortaa text-brand-pink-dark text-lg font-light tracking-wide">
              {{ $t('aboutUs.brandName') }}
            </h3>
            
            <!-- Main Title -->
            <h1 class="font-comfortaa text-brand-dark text-6xl lg:text-7xl font-bold leading-tight">
              {{ $t('aboutUs.title') }}
            </h1>
            
            <!-- Content Paragraphs -->
            <div class="space-y-6 text-brand-dark">
              <p class="font-poppins text-lg leading-relaxed">
                {{ $t('aboutUs.intro') }}
              </p>
              
              <p class="font-poppins text-lg leading-relaxed">
                {{ $t('aboutUs.mission') }}
              </p>
              
              <p class="font-poppins text-lg leading-relaxed">
                {{ $t('aboutUs.values') }}
              </p>
              
              <p class="font-poppins text-lg leading-relaxed font-medium">
                {{ $t('aboutUs.closing') }}
              </p>
            </div>
          </div>
          
          <!-- Images Section -->
          <div class="relative flex justify-center lg:justify-end">
            <div class="relative w-full">
              <!-- Main product image -->
              <div class="relative">
                <img 
                  src="@/assets/about_us/about_us_1.png" 
                  alt="About Us - Main"
                  class="w-full h-auto object-contain"
                />
              </div>
              
              <!-- Decorative elements could be added here if needed -->
            </div>
          </div>
        </div>
      </section>

      <!-- Second Section - Mission & Vision -->
      <section class="py-16">
        <div class="container mx-auto px-4">
          <div class="mission-vision-card">
            <div class="mission-vision-grid">
            <!-- Images Section -->
            <div class="relative flex justify-center lg:justify-start">
              <div class="relative w-full">
                <img 
                  src="@/assets/about_us/about_us_2.png" 
                  alt="Mission & Vision"
                  class="w-full h-auto object-contain"
                />
              </div>
            </div>
            
            <!-- Text Content -->
            <div class="space-y-12">
              <!-- Mission -->
              <div class="mission-vision-item">
                <h2 class="font-comfortaa text-brand-dark text-4xl lg:text-5xl font-bold mb-6 text-right">
                  {{ $t('aboutUs.missionTitle') }}
                </h2>
                <p class="font-poppins text-brand-dark text-lg leading-relaxed text-right">
                  {{ $t('aboutUs.missionText') }}
                </p>
              </div>
              
              <!-- Vision -->
              <div class="mission-vision-item">
                <h2 class="font-comfortaa text-brand-dark text-4xl lg:text-5xl font-bold mb-6 text-right">
                  {{ $t('aboutUs.visionTitle') }}
                </h2>
                <p class="font-poppins text-brand-dark text-lg leading-relaxed text-right">
                  {{ $t('aboutUs.visionText') }}
                </p>
              </div>
            </div>
          </div>
          </div>
        </div>
      </section>

      <!-- Third Section - Corporate Values & What Makes Us Different -->
      <section class="bg-brand-pink-lighter py-16">
        <div class="container mx-auto px-4">
          <div class="values-grid">
            <!-- Corporate Values -->
            <div class="values-section">
              <h2 class="font-comfortaa text-brand-dark text-4xl lg:text-5xl font-bold mb-8">
                Corporate Values
              </h2>
              <ul class="space-y-4">
                <li v-for="(value, index) in corporateValues" :key="index" class="flex items-start">
                  <span class="bullet-point"></span>
                  <p class="font-poppins text-brand-dark text-lg leading-relaxed">
                    {{ value }}
                  </p>
                </li>
              </ul>
            </div>
            
            <!-- What Makes Us Different -->
            <div class="values-section">
              <h2 class="font-comfortaa text-brand-dark text-4xl lg:text-5xl font-bold mb-8">
                What Makes Us Different?
              </h2>
              <div class="mb-6">
                <p class="font-poppins text-brand-dark text-lg leading-relaxed font-medium">
                  We don't just offer a product catalog—we create experiences.
                </p>
              </div>
              <ul class="space-y-4">
                <li v-for="(item, index) in whatMakesUsDifferent" :key="index" class="flex items-start">
                  <span class="bullet-point"></span>
                  <p class="font-poppins text-brand-dark text-lg leading-relaxed">
                    {{ item }}
                  </p>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Diary Promo Banner -->
      <section class="py-8">
        <div class="container mx-auto px-4">
          <PromoBanner
            title=""
            :description="$t('aboutUs.bannerDescription')"
            :primary-button="{ text: $t('aboutUs.shopCollectionBtn') }"
            :secondary-button="{ text: $t('aboutUs.exploreDiariesBtn') }"
            :image="{ src: diaryImage, alt: 'Gift preview' }"
            @primary-click="handleShopCollection"
            @secondary-click="handleExploreDiaries"
          />
        </div>
      </section>

    </main>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/shared/Navbar.vue'
import PromoBanner from '@/components/shared/PromoBanner.vue'
import Footer from '@/components/shared/Footer.vue'
import diaryImage from '@/assets/about_us/about_us_3.png'

// Handle banner interactions
const handleShopCollection = () => {
  console.log('Shopping collection...')
  // Here you can add router navigation or any action
}

const handleExploreDiaries = () => {
  console.log('Exploring diaries...')
  // Here you can add router navigation or any action
}

// Corporate Values
const corporateValues = [
  "Trust & Discretion: every gesture is kept in the privacy it deserves.",
  "Passion: we pour heart and sensuality into every experience.", 
  "Authenticity: every detail reflects a unique, personal bond.",
  "Creativity: we reinvent the art of surprising and enchanting.",
  "Closeness: we support each user so the gift conveys exactly what they feel."
]

// What Makes Us Different
const whatMakesUsDifferent = [
  "We fuse romance and eroticism in one elegant, safe space.",
  "We turn every purchase into a gesture of intimacy and seduction.",
  "We guarantee absolute discretion so desire can be expressed without barriers.",
  "We are more than a store—we are a bridge to intimacy."
]
</script>

<style scoped>
/* Main grid layout */
.main-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

/* Desktop layout */
@media (min-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
  }
}

/* Container styles */
.container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Mission Vision Card */
.mission-vision-card {
  background-color: #A4C1D0; /* brand-blue-light */
  border-radius: 2rem;
  padding: 3rem;
  max-width: 1400px;
  margin: 0 auto;
}

.mission-vision-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
  align-items: center;
}

/* Desktop layout - image left, text right */
@media (min-width: 1024px) {
  .mission-vision-grid {
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
  }
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .main-grid {
    gap: 2rem;
  }
  
  .mission-vision-card {
    padding: 2rem;
  }
  
  .mission-vision-grid {
    gap: 2rem;
  }
  
  /* Change text alignment to center on mobile */
  .mission-vision-item h2,
  .mission-vision-item p {
    text-align: center !important;
  }
}

@media (max-width: 640px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .mission-vision-card {
    padding: 1.5rem;
    border-radius: 1.5rem;
  }
  
  .values-grid {
    gap: 2.5rem;
  }
  
  h1 {
    font-size: 3rem !important;
    line-height: 1.1 !important;
  }
  
  .mission-vision-item h2,
  .values-section h2 {
    font-size: 2.5rem !important;
    line-height: 1.1 !important;
    margin-bottom: 1.5rem !important;
  }
  
  p {
    font-size: 1rem !important;
  }
}

/* Force Comfortaa font for titles */
.mission-vision-item h2,
.values-section h2 {
  font-family: 'Comfortaa', cursive !important;
}

h1 {
  font-family: 'Comfortaa', cursive !important;
}

h3 {
  font-family: 'Comfortaa', cursive !important;
}

/* Force Poppins font for paragraphs */
p {
  font-family: 'Poppins', sans-serif !important;
}

/* Values Section Grid */
.values-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 4rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Desktop layout - two columns */
@media (min-width: 1024px) {
  .values-grid {
    grid-template-columns: 1fr 1fr;
    gap: 5rem;
  }
}

/* Bullet points */
.bullet-point {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: #11181E; /* brand-dark - negro */
  border-radius: 50%;
  margin-top: 12px;
  margin-right: 16px;
  flex-shrink: 0;
}
</style>
