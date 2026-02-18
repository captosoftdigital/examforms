# AdSense Optimization Guide - ExamForms.org

## Maximizing RPM for Education/Exam Niche

---

## UNDERSTANDING RPM

### What is RPM?
```
RPM (Revenue Per Mille) = (Estimated earnings / Page views) × 1000
```

**Example**:
- Earnings: ₹10,000
- Page views: 100,000
- RPM: (10,000 / 100,000) × 1000 = ₹100

### Typical RPM Ranges for Indian Traffic

| Niche | RPM Range (₹) | Our Target |
|-------|---------------|------------|
| Entertainment | 50-100 | - |
| News | 80-150 | - |
| Technology | 100-200 | - |
| **Education/Exams** | 150-250 | ₹200 |
| Finance | 200-400 | - |

**Why Education RPM is Higher**:
- High-intent traffic (students actively searching)
- Competitive exam keywords (government jobs)
- Education advertisers pay premium CPCs
- Low bounce rates (engaged users)

---

## ADSENSE ACCOUNT SETUP

### Step 1: Application Process

**Pre-Requirements**:
- [ ] Domain age: 6 months+ (preferred)
- [ ] Quality content: 20-30 pages minimum
- [ ] Original content (not copied)
- [ ] Clear navigation
- [ ] Privacy policy page
- [ ] About us page
- [ ] Contact page

**Application**:
1. Go to google.com/adsense
2. Enter website URL
3. Submit application
4. Wait 1-3 weeks for review

**Approval Tips**:
- Ensure mobile-friendly design
- Fast loading speed
- No copyright violations
- No prohibited content
- Proper grammar/spelling

### Step 2: Site Verification

```html
<!-- Add AdSense code to <head> section -->
<script data-ad-client="ca-pub-xxxxxxxxxxxxxxxxx" async 
        src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js">
</script>
```

### Step 3: Ad Unit Creation

**Create These Core Ad Units**:

1. **Header Banner** (728×90 or Responsive)
2. **In-Content Rectangle** (336×280 or 300×250)
3. **Sidebar Rectangle** (300×600 or 300×250)
4. **Mobile Anchor** (Sticky footer - mobile only)
5. **In-Feed Native Ads** (for list pages)

---

## AD PLACEMENT STRATEGY

### Desktop Layout

```
┌─────────────────────────────────────────────┐
│  Header                                      │
│  [Banner Ad 728×90]                         │
├─────────────────────────────────────────────┤
│                              ┌──────────────┐
│  H1 Title                    │              │
│                              │  Sidebar Ad  │
│  [In-Content Ad]             │  300×600     │
│                              │              │
│  Content paragraph           │              │
│                              │  [Sticky]    │
│  Important dates table       │              │
│                              └──────────────┘
│  [In-Content Ad]             
│                              
│  How to apply section        
│                              
│  [In-Content Ad]             
│                              
│  FAQs                        
│                              
│  Related Links               
│                              
│  [Footer Ad]                 
└─────────────────────────────────────────────┘
```

### Mobile Layout

```
┌────────────────────┐
│  Header            │
│                    │
│  H1 Title          │
│                    │
│  [In-Content Ad]   │
│  300×250           │
│                    │
│  Content           │
│                    │
│  [In-Content Ad]   │
│  336×280           │
│                    │
│  Important dates   │
│                    │
│  [In-Content Ad]   │
│  300×250           │
│                    │
│  FAQs              │
│                    │
│  Related Links     │
│                    │
│  [Anchor Ad]       │
│  (Sticky footer)   │
└────────────────────┘
```

### Optimal Ad Density

**Policy Compliance**:
- Max 3 ad units per page (standard content)
- Can have more with "valuable content" (1000+ words)
- No ads at very top of page (above title)
- Maintain good content-to-ad ratio

**Our Strategy**:
- 4-6 ad units per page
- Ads after 200-300 words minimum
- Space ads 300-500 words apart
- Never sacrifice UX for ads

---

## AD FORMATS & PERFORMANCE

### 1. Display Ads (Standard)

**Best Performers**:
- 300×250 (Medium Rectangle) - Universal fit
- 336×280 (Large Rectangle) - Higher CTR
- 728×90 (Leaderboard) - Header position
- 300×600 (Half Page) - Sidebar (high viewability)

**Placement**:
- In-content rectangles: Highest CTR
- Sidebar: Good for long content
- Header: High impressions, lower CTR

### 2. Responsive Ads

**Advantages**:
- Adapt to screen size
- Better mobile performance
- Google optimizes automatically

**Implementation**:
```html
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-xxxxxxxxxxxxxxxxx"
     data-ad-slot="1234567890"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
```

### 3. In-Feed Ads (Native)

**Best For**:
- List pages (exam listings)
- Category pages
- Related posts section

**Why Use**:
- Blend with content
- Higher CTR
- Better user experience

### 4. Anchor Ads (Mobile)

**Configuration**:
- Enable in AdSense → Ads → Overview → Anchor ads
- Shows sticky ad at bottom of mobile screen
- Users can close it
- High viewability = high revenue

**Performance**:
- Can increase mobile RPM by 30-50%
- No layout impact
- Google handles frequency

### 5. Auto Ads

**Pros**:
- Google AI places ads automatically
- Tests different placements
- Can discover high-performing spots

**Cons**:
- Less control
- May place too many ads
- Can hurt UX if not monitored

**Our Approach**:
- Start with manual ads
- Enable auto ads after 3 months
- Monitor impact on bounce rate
- Disable if UX degrades

---

## RPM OPTIMIZATION TECHNIQUES

### 1. Content Quality

**High RPM Content**:
- Government job exams (UPSC, SSC, Banking)
- Entrance exams (JEE, NEET, CAT)
- Result pages (high urgency)
- Admit card pages (time-sensitive)

**Lower RPM Content**:
- Syllabus pages (browsing, not urgent)
- Old notifications (outdated)

**Action**: Focus traffic acquisition on high-RPM pages

### 2. Traffic Quality

**Higher Value Traffic**:
- Desktop users (higher CPCs)
- Users from Tier 1 cities (Mumbai, Delhi, Bangalore)
- Older demographics (25-35 years)
- Direct/branded traffic (higher intent)

**Lower Value Traffic**:
- Mobile users (lower CPCs but 85% of traffic)
- Tier 3 cities
- Very young users (16-20 years)

**Action**: Can't control much, but optimize for engagement

### 3. Ad Viewability

**Viewability** = Percentage of ad impressions actually seen

**Improve Viewability**:
- Place ads in content (not sidebar only)
- Sticky sidebar ads (follows scroll)
- Lazy load content, but eager load ads in viewport
- Remove ads below fold if low viewability

**Target**: 70%+ viewability

### 4. Page Speed

**Impact on RPM**:
- Slow pages = fewer ad impressions
- Users leave before ads load
- Google penalizes slow sites

**Optimization**:
- Lazy load images
- Defer non-critical JS
- Use CDN
- Compress assets
- **Target**: < 2 second load time

### 5. User Engagement

**Metrics That Matter**:
- Time on page (target: 90+ seconds)
- Pages per session (target: 4+)
- Bounce rate (target: <60%)

**How to Improve**:
- High-quality, useful content
- Internal linking (related exams)
- Clear navigation
- Fast page loads

**Why It Matters**: 
- More engagement = more ad impressions
- Lower bounce = higher ad viewability
- Google shows better ads to engaged users

---

## ADVANCED OPTIMIZATION

### 1. Ad Balance

**Feature**: AdSense → Optimization → Ad Balance

**What It Does**:
- Shows fewer, higher-paying ads
- Reduces ad clutter
- Can increase RPM by reducing low-value impressions

**How to Use**:
1. Wait for 2-3 months of data
2. Experiment with slider (start at 10% reduction)
3. Monitor impact on revenue
4. Find optimal balance

### 2. Blocking Controls

**Block Low-Paying Ad Categories**:
- AdSense → Blocking Controls → General Categories

**Categories to Consider Blocking** (test first):
- Dating
- Gambling (if low CPC in your region)
- Low-quality apps

**Why**: Blocking low-CPC ads makes room for high-CPC ads

**Caution**: Don't block too many (reduces fill rate)

### 3. Ad Review Center

**Review Specific Ads**:
- AdSense → Blocking Controls → Ad Review Center

**Actions**:
- Block irrelevant ads
- Block competitors (if any)
- Block low-quality ads

**Frequency**: Weekly review for first 3 months

### 4. Placement Targeting

**Allow Advertisers to Target Your Placements**:
- AdSense → Account → Settings → Placement Targeting
- Enable it

**Why**: Premium advertisers can bid on your inventory directly (higher CPCs)

### 5. Link Ads

**Enable Text Link Ads**:
- Can show alongside display ads
- Sometimes higher CTR
- Works well in content

**Placement**: 
- After H2 headings
- Between content paragraphs

---

## RPM BENCHMARKING & TRACKING

### Daily Metrics to Track

```
Date: Jan 15, 2026
Page Views: 100,000
Impressions: 450,000
Clicks: 900
CTR: 0.2%
CPC: ₹15
Earnings: ₹13,500
RPM: ₹135
```

**Analysis**:
- RPM below target (₹200)
- Investigate: Low CPC or low impressions/PV?
- Action: Test more ad units or improve content quality

### Weekly Review

**Questions to Ask**:
1. Which pages have highest RPM? (double down on similar content)
2. Which pages have lowest RPM? (improve or deprioritize)
3. Are mobile and desktop RPMs very different? (optimize separately)
4. Which traffic sources have best RPM? (focus growth there)

### Monthly Optimization

**Actions**:
1. Review Ad Balance (adjust if needed)
2. Block bottom 10% performing ad categories
3. Test new ad formats
4. Analyze top competitors' ad strategies
5. Update ad placements based on heatmaps

---

## POLICY COMPLIANCE (CRITICAL)

### Absolute Don'ts

**Never**:
- Click your own ads
- Ask others to click
- Place ads on pages with prohibited content
- Use misleading headlines to get clicks
- Auto-refresh pages to inflate impressions
- Place more than 3 link units per page
- Cover content with ads
- Use floating/pop-up ads (except anchor)

**Prohibited Content**:
- Adult content
- Violent content
- Hacking/cracking content
- Fake documents/degrees
- Illegal content

### Best Practices

**Do**:
- Label ads clearly (not required but good practice)
- Maintain content quality
- Respond to policy violations immediately
- Keep site architecture clean
- Monitor invalid click activity
- Use compliant ad placements

### If Account is Suspended

**Actions**:
1. Don't panic
2. Read violation notice carefully
3. Fix the issue
4. Submit appeal with explanation
5. If rejected, try Ezoic or Mediavine

**Prevention**: 
- Monthly policy review
- Use multiple domains (backup)
- Separate AdSense accounts where possible

---

## REVENUE SCALING TIMELINE

### Month 1-3: Learning Phase
- **RPM**: ₹100-150 (expect lower)
- **Why**: New site, learning ad placements, low authority
- **Action**: Focus on traffic, not RPM

### Month 4-6: Optimization Phase
- **RPM**: ₹150-180
- **Why**: Better placements, growing authority, more data
- **Action**: Optimize based on data, block low-performing categories

### Month 7-12: Growth Phase
- **RPM**: ₹180-220
- **Why**: Domain authority increasing, premium advertisers discover site
- **Action**: Scale traffic, maintain quality

### Month 13+: Mature Phase
- **RPM**: ₹200-250+
- **Why**: Established site, repeat users, high engagement, premium inventory
- **Action**: Maintain quality, test new ad formats, consider Ad Manager

---

## ALTERNATIVE MONETIZATION (Backup Plans)

### 1. Ezoic (If AdSense Suspended)

**Pros**:
- Similar to AdSense
- AI-optimized ad placements
- Good for 10K+ sessions/month

**Cons**:
- Slightly more setup
- Performance impact if not configured well

**RPM**: Similar to AdSense (₹150-250)

### 2. Media.net

**Pros**:
- Yahoo/Bing network
- Contextual ads
- Works alongside AdSense

**Cons**:
- Requires 5K+ daily visitors for approval
- Lower RPM than AdSense for Indian traffic

**RPM**: ₹80-150

### 3. Google Ad Manager (At Scale)

**When to Use**: 
- 50M+ page views/month
- Want to sell direct ads
- Need more control

**Benefit**: 
- Can run AdSense + direct ads
- Higher revenue potential (20-30% increase)
- More reporting features

---

## ADSENSE CHECKLIST

### Pre-Launch
- [ ] Privacy policy page created
- [ ] About page created
- [ ] Contact page created
- [ ] Quality content (30+ pages)
- [ ] Mobile-friendly design
- [ ] Fast loading speed (<3s)
- [ ] No prohibited content

### Post-Approval
- [ ] Ad units created (5-6 types)
- [ ] Ads placed on all pages
- [ ] Mobile anchor ads enabled
- [ ] Auto ads tested (optional)
- [ ] Analytics linked to AdSense

### Ongoing (Weekly)
- [ ] Check earnings and RPM
- [ ] Review ad performance by page
- [ ] Block poor-performing ad categories
- [ ] Test new ad placements
- [ ] Monitor policy compliance

### Monthly
- [ ] Ad balance optimization
- [ ] Competitor ad strategy review
- [ ] Revenue analysis by traffic source
- [ ] RPM benchmarking
- [ ] Goal: Increase RPM by 5-10% monthly

---

## FINAL RPM TARGET STRATEGY

**Conservative**: ₹150 RPM
- Achievable from Month 6
- Low risk assumption
- Requires 667M PVs for ₹10Cr

**Base Case**: ₹200 RPM
- Target from Month 12
- Realistic with optimization
- Requires 500M PVs for ₹10Cr

**Optimistic**: ₹250 RPM
- Achievable at scale (18+ months)
- High-quality traffic + optimization
- Requires 400M PVs for ₹10Cr

**Strategy**: 
- Plan for ₹200 RPM
- Focus equally on traffic growth and RPM optimization
- Every ₹10 increase in RPM = 20M fewer PVs needed

