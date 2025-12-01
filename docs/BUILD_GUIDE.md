# Bioworld Ecosystem Build Guide

This guide details how to customize and implement the Bioworld MMORPG ecosystem using Unreal Engine 5.x. It covers the core scientific mechanics, dynamic system architecture, economic layers, and visual customization.

---

## Table of Contents

1. [Core Scientific Mechanics](#1-core-scientific-mechanics-learning--doing)
2. [Dynamic System Architecture](#2-dynamic-system-architecture-holarchy-and-systems)
3. [Economic and Communication Layers](#3-economic-and-communication-layers)
   - [Biocoin Economy System](#31-biocoin-economy-system)
   - [Token Lockdown Mechanics](#token-lockdown-mechanics)
   - [Anti-Black Market Detection](#anti-black-market-detection)
   - [Economic Sinks & Disincentives](#economic-sinks--disincentives)
   - [Enforcement & Reset Integration](#enforcement--reset-integration)
4. [Visual and Environmental Realism](#4-visual-and-environmental-realism)
5. [Build Checklist](#5-build-checklist)
6. [Prioritized Coding Tasks](#6-prioritized-coding-tasks)

---

## 1. Core Scientific Mechanics (Learning & Doing)

The initial gameplay centers on biotechnology challenges implemented through scalable, functional game systems.

### 1.1 Protein Discovery and Design

The central mechanical loop involves the **protein folding problem**: taking an amino acid sequence and determining its complex 3D shape.

#### AI Integration

Players utilize AI models (similar to AlphaFold or generative AI techniques) to:
- Predict protein structure from amino acid sequences
- Design entirely new proteins (e.g., synthetic antibodies, plastic-breaking enzymes)

**Implementation:**
- Core logic in specialized **C++ classes** or **Blueprint Actor components**
- Player input (sequence/design goal) triggers simulation of the AI process
- Results returned as predicted structures with confidence scores

```cpp
// Example: Protein Prediction Component
UCLASS()
class UProteinPredictionComponent : public UActorComponent
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable)
    FProteinStructure PredictStructure(const FString& AminoAcidSequence);
    
    UFUNCTION(BlueprintCallable)
    FProteinDesign GenerateNovelProtein(const FString& Purpose, const FDesignConstraints& Constraints);
};
```

#### Data Management

Store and manage protein data efficiently using:

| Data Type | Unreal Structure | Purpose |
|-----------|------------------|---------|
| Sequences | Data Tables | Tabular organization of amino acid sequences |
| Structures | USTRUCT | 3D structure data with coordinates |
| Functions | Data Tables | Protein function mappings |
| Validation Results | USTRUCT | Wet lab validation outcomes |

**Example USTRUCT:**
```cpp
USTRUCT(BlueprintType)
struct FProteinData
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString ProteinID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString AminoAcidSequence;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float ConfidenceScore;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<FVector> AtomicCoordinates;
};
```

### 1.2 Lab Work and Validation

Even with high AI accuracy, simulated "wet lab" data must occasionally be used for crucial validation.

#### Events and Failure States

Manage real scientific challenges via **Blueprint Events**:
- Data standardization issues → Failed experiment events
- Ethical concerns → Review board triggers
- Non-standardized data → Reduced generalizability

**Blueprint Event Examples:**
- `OnExperimentComplete`
- `OnValidationFailed`
- `OnEthicalReviewRequired`
- `OnDataStandardizationError`

#### Visual Customization

Use **Material Parameter Collections (MPCs)** for lab environments:

```
MPC_LabEnvironment
├── BaseColor (Vector)
├── EmissiveIntensity (Scalar)
├── ContaminationLevel (Scalar)
└── BiohazardTint (Vector)
```

Benefits:
- Globally alter material properties across lab setups
- Create visual diversity without extensive manual material creation
- Dynamic feedback for experiment states (success/failure colors)

---

## 2. Dynamic System Architecture (Holarchy and Systems)

Bioworld functions as a **highly dynamic, collaborative, and competitive environment** modeled as a holarchy.

### 2.1 System Components and Structure

The complex nature arises from simple components following simple rules, leading to **emergent behavior**.

| Component | Description | Implementation |
|-----------|-------------|----------------|
| **Agents** | Objects with properties/behaviors (diseases, labs, players) | Actor Classes |
| **Networks** | Linked pathways (APIs, communication channels) | Interface Systems |
| **Layers** | Global parameters governing behavior | Game Instance / Subsystems |

### 2.2 Player Organizations (Holons)

Player corporations are **higher-order entities** composed of interacting research teams and financial systems.

**Implementation using Component Hierarchy:**

```
ACorporationActor
├── UResearchTeamComponent (Child 1)
│   ├── ULabComponent
│   └── UScientistComponent[]
├── UResearchTeamComponent (Child 2)
│   └── ...
├── UFinancialSystemComponent
│   ├── UTreasuryComponent
│   └── UPatentPortfolioComponent
└── UReputationComponent
```

Changes to parent components immediately affect all children.

### 2.3 Procedural Content Generation (PCG)

Create vast, realistic bioworld landscapes using the PCG Framework.

#### PCG Setup Steps

1. **Configure PCG Volume**
   - Locate and add PCG Volume to level
   - Configure to fit landscape dimensions
   - Set appropriate bounds for generation

2. **Create PCG Graph**
   ```
   PCG_BioworldTerrain
   ├── Surface Sampler (Sample landscape height/density)
   ├── Point Filter (Elevation-based filtering)
   ├── Static Mesh Spawner (3D assets)
   └── Foliage Spawner (Plants/vegetation)
   ```

3. **Elevation-Based Rules**
   - Generate vegetation only at elevations > threshold
   - Place lab structures on flat terrain
   - Distribute biohazard zones based on slope

4. **Asset Integration**
   - Import Megascans assets with **Nanite** enabled
   - High-complexity assets without performance compromise
   - Real-time rendering optimization

#### Example PCG Node Configuration

| Node | Parameter | Value |
|------|-----------|-------|
| Surface Sampler | Sample Density | 100 points/m² |
| Point Filter | Min Elevation | 50m |
| Point Filter | Max Slope | 30° |
| Static Mesh Spawner | Mesh | SM_LabModule_01 |

---

## 3. Economic and Communication Layers

Integrate sophisticated economic and legal components into the player experience.

### 3.1 Biocoin Economy System

Bioworld uses **Biocoin** as the core in-game cryptocurrency with a closed-loop, non-transferable design.

#### Conversion Mechanics

| Conversion | Rate | Direction |
|------------|------|-----------|
| USD → Biocoin | 4x multiplier | $1 USD = 4 Biocoin |
| Biocoin → USD | Not allowed | Non-transferable outside game |

**Design Principles:**
- High in-game purchasing power for assets, lab expansions, API upgrades
- Closed-loop system recirculates value through marketplaces
- Prevents external cash-outs to maintain ecosystem integrity
- Focus on internal progression over speculation

#### Biocoin Acquisition Methods

| Source | Description | Implementation |
|--------|-------------|----------------|
| Initial Deposits | Fiat/crypto converts at 4x rate | Secure payment gateway |
| Scientific Breakthroughs | Protein discoveries, validations | `OnBreakthroughComplete` event |
| Mech Challenge Wins | PvP/PvE competition prizes | Match result callbacks |
| Ad Interactions | Progression-only rewards | Optional engagement system |
| Lab Trades | Marketplace transactions | `ReplicatedUsing` sync |

#### Biocoin Sinks (Value Recirculation)

Maintain economic stability through demand-driven sinks:

| Sink | Cost Range | Purpose |
|------|------------|---------|
| Reset Votes | Variable stake | Community governance |
| Asset Uplifts (>10MB) | Premium tier | High-quality asset hosting |
| MCP Enhancements | Tiered pricing | Premium progression boosts |
| Epochal Research | High stakes | Major scientific milestones |
| Branded Progression | Partnership rates | Sponsored advancement |

#### Implementation: Biocoin Subsystem

```cpp
UCLASS()
class UBiocoinSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Conversion (locked to 4x rate)
    UFUNCTION(BlueprintCallable)
    int64 ConvertToBiocoin(float USDAmount) { return FMath::FloorToInt64(USDAmount * 4.0f); }
    
    // Balance management
    UPROPERTY(ReplicatedUsing=OnRep_Balance)
    int64 PlayerBalance;
    
    UFUNCTION()
    void OnRep_Balance();
    
    // Transaction validation
    UFUNCTION(BlueprintCallable)
    bool ProcessTransaction(const FBiocoinTransaction& Transaction);
    
    // Royalty distribution
    UFUNCTION(BlueprintCallable)
    void DistributeScientificRoyalties(const FString& BreakthroughID, const TArray<FLabContributor>& Contributors);
};
```

#### Biocoin Data Structures

```cpp
USTRUCT(BlueprintType)
struct FBiocoinTransaction
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString TransactionID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString SenderID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString ReceiverID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int64 Amount;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    ETransactionType Type; // Trade, Royalty, Reward, Sink
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FDateTime Timestamp;
};

USTRUCT(BlueprintType)
struct FLabContributor
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString PlayerID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString LabID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float ContributionPercent; // Royalty share
};
```

#### Lab Development & Utility

Biocoin powers all lab progression:

| Feature | Biocoin Cost | Description |
|---------|--------------|-------------|
| Hire Collaborators | 50-500 | Add team members to lab |
| Ecosystem Expansion Bids | 1000+ | E-commerce hubs, schools |
| Leadership Staking | Variable | Proposal rights (subject to ethical votes) |
| Equipment Upgrades | 100-2000 | Enhanced simulation capabilities |

#### Governance & Stability

**Reset Points (Extinction Events):**
- Community votes using pooled Biocoin stakes
- Prune economic imbalances and monopolies
- Enforce moral guidelines

**Reputation Multipliers:**

| Reputation Level | Biocoin Yield Multiplier |
|------------------|--------------------------|
| Standard Lab | 1.0x |
| Ethical Lab | 1.5x |
| Sustainable Innovation | 1.75x |
| Community Leader | 2.0x |

**Implementation: Governance Interface**

```cpp
UINTERFACE(MinimalAPI, Blueprintable)
class UBiocoinGovernanceInterface : public UInterface
{
    GENERATED_BODY()
};

class IBiocoinGovernanceInterface
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    bool ProposeResetVote(int64 StakeAmount, const FString& Proposal);
    
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    void CastVote(const FString& ProposalID, bool bApprove, int64 VoteWeight);
    
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    float GetReputationMultiplier(const FString& LabID);
};
```

#### Token Lockdown Mechanics

Biocoin operates on a **closed-loop blockchain** isolated from external networks to prevent unauthorized transfers.

**Server-Side Wallet Architecture:**

| Component | Function | Security Layer |
|-----------|----------|----------------|
| Mint Server | Creates account-bound tokens on fiat deposit | Server-only access |
| Identity Binding | Tokens tied to in-game identity | Non-fungible, non-transferable |
| Geofencing | Blocks cross-game/wallet exports | Server-enforced |
| Smart Contracts | Real-time transaction auditing | Auto-freeze suspicious patterns |

**Authentication Requirements:**

```cpp
USTRUCT(BlueprintType)
struct FBiocoinAuthContext
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString PlayerID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString BiometricHash; // Device biometric verification
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString MFAToken; // Multi-factor authentication
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString SessionID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString GeoRegion; // Geofencing validation
};

UCLASS()
class UBiocoinSecuritySubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Validate transaction with full auth context
    UFUNCTION(BlueprintCallable)
    bool ValidateTransaction(const FBiocoinTransaction& Transaction, const FBiocoinAuthContext& AuthContext);
    
    // Check for suspicious patterns (RMT indicators)
    UFUNCTION(BlueprintCallable)
    ESecurityStatus AnalyzeTransactionPattern(const FString& PlayerID, const TArray<FBiocoinTransaction>& RecentTransactions);
    
    // Auto-freeze account on detection
    UFUNCTION(BlueprintCallable)
    void FreezeAccount(const FString& PlayerID, const FString& Reason);
};
```

#### Anti-Black Market Detection

Implement anomaly detection to identify and prevent Real Money Trading (RMT).

**Detection Algorithms:**

| Pattern | Indicators | Action |
|---------|------------|--------|
| Rapid Bulk Trades | High volume in short timeframe | Auto-freeze + review |
| New Player Dumping | Low-level account selling high-value assets | Flag + temporary lab freeze |
| VPN Cluster Trading | Multiple trades from same VPN exit nodes | Network analysis + ban wave |
| Unnatural Velocity | Transaction speed exceeds human capability | Bot detection + quarantine |

**Implementation: Anomaly Detection System**

```cpp
UENUM(BlueprintType)
enum class EAnomalyType : uint8
{
    None,
    RapidBulkTrade,
    NewPlayerDump,
    VPNCluster,
    UnnatualVelocity,
    NetworkCollusion
};

USTRUCT(BlueprintType)
struct FPlayerTradeProfile
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString PlayerID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 AccountAgeDays;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float AverageTradeVolume;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float TradeVelocity; // Trades per hour
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<FString> TradingPartners;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float RiskScore; // 0.0 - 1.0
};

UCLASS()
class UAnomalyDetectionSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Analyze player trading behavior
    UFUNCTION(BlueprintCallable)
    EAnomalyType DetectAnomaly(const FPlayerTradeProfile& Profile);
    
    // Map trading networks to expose RMT guilds
    UFUNCTION(BlueprintCallable)
    TArray<FString> AnalyzeTradingNetwork(const FString& PlayerID, int32 Depth);
    
    // Community moderation queue
    UFUNCTION(BlueprintCallable)
    void SubmitPlayerReport(const FString& ReporterID, const FString& SuspectID, const FString& Evidence);
    
    // Biocoin bounty for verified busts
    UFUNCTION(BlueprintCallable)
    void AwardBounty(const FString& ReporterID, int64 BountyAmount);
};
```

**Community Moderation System:**

| Feature | Description | Reward |
|---------|-------------|--------|
| Player Reports | Submit evidence of RMT activity | Queue for review |
| Verified Busts | Confirmed violations | Biocoin bounty |
| AI Network Graphs | Map trading networks | Expose guild collusion |
| High-Rep Priority | Trusted labs get trade priority | Visibility for ethical play |

#### Economic Sinks & Disincentives

Aggressive sinks devalue black market supply while rewarding legitimate play.

**Dynamic Pricing System:**

```cpp
UCLASS()
class UDynamicPricingSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Adjust prices based on ecosystem health
    UFUNCTION(BlueprintCallable)
    float CalculateDynamicPrice(const FString& AssetID, float BasePrice);
    
    // Inflate RMT targets to uneconomic levels
    UFUNCTION(BlueprintCallable)
    float GetInflationMultiplier(EAssetCategory Category);
    
    // Mandatory cool-down on large trades
    UFUNCTION(BlueprintCallable)
    bool CanExecuteTrade(const FString& PlayerID, int64 TradeAmount);
    
    // 24-hour hold for large transactions
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int64 LargeTradeThreshold = 10000;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float CooldownHours = 24.0f;
};
```

**Trade Restrictions:**

| Restriction | Threshold | Cooldown |
|-------------|-----------|----------|
| Standard Trade | < 1,000 Biocoin | None |
| Medium Trade | 1,000 - 10,000 | 1 hour |
| Large Trade | 10,000 - 100,000 | 24 hours |
| Massive Trade | > 100,000 | 72 hours + manual review |

#### Enforcement & Reset Integration

Escalating penalties for violations with community governance oversight.

**Penalty Tiers:**

| Offense | Penalty | Duration |
|---------|---------|----------|
| First Offense | Asset quarantine + partial Biocoin burn | 7 days |
| Second Offense | Lab freeze + reputation penalty | 30 days |
| Third Offense | Lab eviction via ethical vote | Permanent |
| Threshold Breach | Full account reset | Immediate |

**Implementation: Enforcement System**

```cpp
UENUM(BlueprintType)
enum class EPenaltyTier : uint8
{
    Warning,
    FirstOffense,
    SecondOffense,
    ThirdOffense,
    ThresholdBreach
};

USTRUCT(BlueprintType)
struct FViolationRecord
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString PlayerID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    EPenaltyTier CurrentTier;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<FString> ViolationHistory;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int64 TotalBiocoinBurned;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bLabEvicted;
};

UCLASS()
class UEnforcementSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Apply penalty based on violation tier
    UFUNCTION(BlueprintCallable)
    void ApplyPenalty(const FString& PlayerID, EPenaltyTier Tier);
    
    // Quarantine assets pending review
    UFUNCTION(BlueprintCallable)
    void QuarantineAssets(const FString& PlayerID, const TArray<FString>& AssetIDs);
    
    // Burn Biocoin as penalty
    UFUNCTION(BlueprintCallable)
    void BurnBiocoin(const FString& PlayerID, int64 Amount);
    
    // Trigger community eviction vote
    UFUNCTION(BlueprintCallable)
    void InitiateEvictionVote(const FString& TargetPlayerID, const FString& Evidence);
    
    // Publish anonymized bust statistics
    UFUNCTION(BlueprintCallable)
    FEnforcementStats GetPublicStats();
};
```

**Transparency Features:**

| Feature | Purpose |
|---------|---------|
| Anonymized Bust Stats | Deter participation via public ledger |
| Audited Channels | High-volume traders restricted to whitelists |
| Ethical Vote Records | Community governance transparency |
| Real-time Dashboards | Ecosystem health visibility |

### 3.2 Economic Simulation and Replication

The economy simulates financial markets using:
- **Reinforcement Learning (RL)** for trading algorithms
- **Game Theory** for strategic decision-making

#### Network Replication

For multiplayer synchronization:

1. **Enable Replicates** on economic Actors (Details Panel)
2. **Use ReplicatedUsing** for frequently changing properties:

```cpp
UPROPERTY(ReplicatedUsing=OnRep_MarketValue)
float MarketValue;

UFUNCTION()
void OnRep_MarketValue()
{
    // Called when MarketValue updates across network
    UpdateMarketUI();
    NotifyPriceChange();
}
```

#### Properties to Replicate

| Property | Replication Type | Callback |
|----------|------------------|----------|
| Market Performance | ReplicatedUsing | `OnRep_Performance` |
| Patent Status | ReplicatedUsing | `OnRep_PatentApproval` |
| Corporation Treasury | Replicated | - |
| Trade Orders | ReplicatedUsing | `OnRep_TradeExecuted` |

### 3.2 In-Game Writing and NLP

Players use NLP tools to generate:
- Scientific papers
- Marketing copy
- Research documentation

**UI Implementation:**
- Build with **Widget Blueprints**
- Display NLP output in formatted text widgets
- Support for rich text formatting (citations, formulas)

```
WBP_ResearchPaperWriter
├── TextInput_Abstract
├── TextInput_Methods
├── TextInput_Results
├── Button_GenerateWithAI
└── RichTextBlock_Output
```

### 3.3 Interactions and Patents (Legal/Ethical)

Manage patent securing and ethical dilemmas via **Blueprint Interfaces**.

#### Interface Design

```cpp
UINTERFACE(MinimalAPI, Blueprintable)
class UPatentInteractionInterface : public UInterface
{
    GENERATED_BODY()
};

class IPatentInteractionInterface
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    bool SubmitPatentApplication(const FPatentData& Patent);
    
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    FPatentStatus CheckPatentStatus(const FString& PatentID);
};
```

**Implementing Actors:**
- `APatentOfficeActor` - Processes patent applications
- `AEthicalReviewBoardActor` - Handles bias/transparency reviews
- `APlayerLabActor` - Communicates with both without class references

---

## 4. Visual and Environmental Realism

Visual fidelity is crucial for immersive biotechnology environments.

### 4.1 Large World Management

Handle MMORPG scale using **World Partition**.

#### Setup Steps

1. **Enable World Partition**
   - World Settings → Enable World Partition
   - Save level

2. **Convert Level**
   - Tools → Convert Level to World Partition
   - Configure cell size (recommended: 12800 units)

3. **Configure Streaming**
   - Set streaming distance based on player visibility
   - Enable HLOD for distant cells

| Setting | Recommended Value |
|---------|-------------------|
| Cell Size | 12800 units |
| Loading Range | 3 cells |
| HLOD Enabled | Yes |

### 4.2 Landscape Material Blending

Create realistic terrain using auto-blend materials.

#### Material Function Setup

1. **Create Base Material Function**
   - Height-based layer blending
   - Slope-based material selection

2. **Convert Constants to Parameters**

| Parameter | Type | Purpose |
|-----------|------|---------|
| `Ground_Minimum` | Scalar | Minimum height for ground layer |
| `Ground_Maximum` | Scalar | Maximum height for ground layer |
| `FallOff` | Scalar | Blend falloff distance |
| `SlopeThreshold` | Scalar | Slope angle for rock transition |

3. **Apply Material Instance**
   - Create Material Instance from base
   - Apply to all landscape partitions
   - Adjust parameters per biome

### 4.3 Dynamic Visuals

#### Emissive Materials

For glowing biological agents and energy sources:

```
M_BiologicalAgent_Emissive
├── Base Color (Texture Sample)
├── Emissive Color (Vector Parameter)
├── Emissive Intensity (Scalar Parameter)
└── Emissive → Multiplied → Emissive Output
```

#### Lumen Integration

When **Lumen** (dynamic global illumination) is enabled:
- Emissive materials dynamically influence surroundings
- Real-time light bouncing from biological specimens
- Enhanced visual spectacle for energy sources

#### Niagara Particle Systems

For complex scientific visualizations:

| Effect | System Name | Use Case |
|--------|-------------|----------|
| Protein Folding | NS_ProteinFold | Visualize folding animation |
| DNA Helix | NS_DNASpiral | Genetic sequence display |
| Molecular Bonds | NS_MolecularBond | Chemical reactions |
| Energy Transfer | NS_EnergyPulse | Cellular processes |

---

## 5. Build Checklist

Use this checklist when implementing Bioworld components:

### Phase 1: Core Systems

- [ ] Create `UProteinPredictionComponent` for AI integration
- [ ] Set up Data Tables for protein sequences
- [ ] Define USTRUCTs for protein data
- [ ] Implement Blueprint Events for lab validation
- [ ] Create MPC for lab environment visuals

### Phase 2: Architecture

- [ ] Design Actor hierarchy for corporations
- [ ] Implement component relationships (parent/child)
- [ ] Set up PCG Volume for terrain generation
- [ ] Configure PCG graph with samplers and filters
- [ ] Enable Nanite for high-detail assets

### Phase 3: Economy & Biocoin

- [ ] Enable replication on economic Actors
- [ ] Implement `ReplicatedUsing` callbacks
- [ ] Create Widget Blueprints for NLP output
- [ ] Define Blueprint Interfaces for patents
- [ ] Set up patent/ethics Actor communication

#### Biocoin Core
- [ ] Implement `UBiocoinSubsystem` with 4x conversion rate
- [ ] Create `FBiocoinTransaction` and `FLabContributor` structs
- [ ] Set up server-side wallet minting (account-bound tokens)
- [ ] Implement `UBiocoinGovernanceInterface` for voting

#### Token Lockdown
- [ ] Implement `FBiocoinAuthContext` for MFA/biometric auth
- [ ] Create `UBiocoinSecuritySubsystem` for transaction validation
- [ ] Set up geofencing blocks for cross-game exports
- [ ] Configure smart contract audit rules

#### Anti-Black Market
- [ ] Implement `UAnomalyDetectionSubsystem` for RMT detection
- [ ] Create `FPlayerTradeProfile` for behavior analysis
- [ ] Set up trading network graph analysis
- [ ] Implement community moderation queue with bounties

#### Economic Sinks
- [ ] Implement `UDynamicPricingSubsystem` for price adjustments
- [ ] Configure trade cooldowns (1h/24h/72h tiers)
- [ ] Set up large trade thresholds and manual review

#### Enforcement
- [ ] Implement `UEnforcementSubsystem` with penalty tiers
- [ ] Create `FViolationRecord` for tracking offenses
- [ ] Set up asset quarantine and Biocoin burn mechanics
- [ ] Implement community eviction vote system
- [ ] Configure anonymized bust stats dashboard

### Phase 4: Visuals

- [ ] Enable World Partition
- [ ] Convert level and configure cell size
- [ ] Create landscape material functions
- [ ] Set up height/slope parameters
- [ ] Create emissive materials for bio-agents
- [ ] Enable Lumen global illumination
- [ ] Set up Niagara systems for effects

---

## Summary

Customizing the Bioworld ecosystem involves treating each complex concept (protein folding, economic competition) as a defined set of:
- **Inputs** (player actions, sequences)
- **Outputs** (predictions, structures, market results)
- **Rules** (validation logic, economic formulas)
- **Triggers** (events, callbacks)

These are implemented using Unreal Engine's:
- Data Tables & USTRUCTs
- Blueprints & C++ Classes
- Blueprint Interfaces
- Procedural Content Generation
- World Partition
- Lumen & Nanite

The result is a self-assembling machine: simple rules for individual gears (components and systems) combine to create the massive, complex, and evolving Bioworld ecosystem.

---

## 6. Prioritized Coding Tasks

Use MoSCoW prioritization (Must/Should/Could) with modular builds. Start with single-player prototypes before multiplayer scaling. Track via GitHub Projects with Copilot-assisted test generation per module.

### Must-Have (Core Loop) — Weeks 1-4

These tasks establish the fundamental gameplay loop required for a playable prototype.

#### Week 1-2: Foundation

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Player Account System** | Basic player profile with authentication | `PlayerCore` | P0 |
| **Asset Upload System** | 10MB vetted uploader with validation (file types, size limits) | `AssetManager` | P0 |
| **Cloud Storage Integration** | Connect asset uploader to cloud buckets (S3/GCS) | `AssetManager` | P0 |
| **MCP/API Slot Integration** | Player profile slots for model endpoints | `PlayerCore` | P0 |

```cpp
// PlayerCore Module - Account System
UCLASS()
class UPlayerAccountSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable)
    bool CreateAccount(const FPlayerRegistration& Registration);
    
    UFUNCTION(BlueprintCallable)
    bool AuthenticatePlayer(const FString& PlayerID, const FAuthCredentials& Credentials);
    
    UFUNCTION(BlueprintCallable)
    FPlayerProfile GetPlayerProfile(const FString& PlayerID);
};

// AssetManager Module - Upload System
UCLASS()
class UAssetUploadSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Validate asset before upload (10MB limit, allowed types)
    UFUNCTION(BlueprintCallable)
    EAssetValidationResult ValidateAsset(const FString& FilePath);
    
    // Upload to cloud storage
    UFUNCTION(BlueprintCallable)
    void UploadAsset(const FString& FilePath, const FOnUploadComplete& Callback);
    
    UPROPERTY(EditAnywhere)
    int64 MaxFileSizeBytes = 10 * 1024 * 1024; // 10MB
    
    UPROPERTY(EditAnywhere)
    TArray<FString> AllowedFileTypes = {".fbx", ".obj", ".png", ".jpg", ".wav"};
};
```

#### Week 2-3: Lab Building

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Modular Lab Class** | Base class for lab placement and management | `LabSystem` | P0 |
| **Asset Placement** | Place uploaded assets in lab space | `LabSystem` | P0 |
| **Basic Simulation** | Resource generation and experiment logic | `SimulationCore` | P0 |
| **Lab UI Dashboard** | Management interface for lab operations | `LabUI` | P0 |

```cpp
// LabSystem Module - Core Lab Class
UCLASS()
class APlayerLab : public AActor
{
    GENERATED_BODY()
    
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString LabID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString OwnerPlayerID;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TArray<FPlacedAsset> PlacedAssets;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FLabResources Resources;
    
    // Place asset in lab
    UFUNCTION(BlueprintCallable)
    bool PlaceAsset(const FString& AssetID, FTransform Transform);
    
    // Run simulation tick
    UFUNCTION(BlueprintCallable)
    void SimulateTick(float DeltaTime);
    
    // Generate resources based on lab configuration
    UFUNCTION(BlueprintCallable)
    FResourceOutput CalculateResourceGeneration();
};
```

#### Week 3-4: Biocoin & Governance

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Biocoin Minting** | Server-side 4x conversion from fiat gateway | `BiocoinCore` | P0 |
| **Account-Bound Tokens** | Smart contract lockdown (no external transfers) | `BiocoinCore` | P0 |
| **Voting UI** | Simple interface for lab proposals/resets | `GovernanceUI` | P0 |
| **Extinction Event Prototype** | Threshold triggers for flagged mechanics | `GovernanceCore` | P0 |

```cpp
// BiocoinCore Module - Minting System
UCLASS()
class UBiocoinMintingSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Convert fiat to Biocoin at 4x rate (server-side only)
    UFUNCTION(BlueprintCallable, Server)
    FMintResult MintFromFiat(const FString& PlayerID, float FiatAmount, const FPaymentConfirmation& Payment);
    
    // Verify account binding (non-transferable check)
    UFUNCTION(BlueprintCallable)
    bool IsTokenAccountBound(const FString& TokenID, const FString& PlayerID);
    
    // Lock token to prevent any external transfer attempt
    UFUNCTION(BlueprintCallable)
    void EnforceTokenLockdown(const FString& TokenID);
    
private:
    const float CONVERSION_RATE = 4.0f;
};

// GovernanceCore Module - Voting System
UCLASS()
class UVotingSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable)
    FString CreateProposal(const FString& ProposerID, const FProposalData& Proposal);
    
    UFUNCTION(BlueprintCallable)
    bool CastVote(const FString& ProposalID, const FString& VoterID, bool bApprove, int64 StakeAmount);
    
    UFUNCTION(BlueprintCallable)
    bool CheckThresholdAndExecute(const FString& ProposalID);
    
    // Trigger extinction event on flagged mechanics
    UFUNCTION(BlueprintCallable)
    void TriggerExtinctionEvent(const FString& Reason, const TArray<FString>& AffectedLabs);
};
```

---

### Should-Have (Persistence & Multiplayer) — Weeks 5-8

Expand to multiplayer with persistent world state and collaborative features.

#### Week 5-6: Travel & Collaboration

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Wormhole Travel System** | Fast travel with zoning between regions | `TravelSystem` | P1 |
| **Real-time Co-op Lab Editing** | WebSocket-based collaborative editing | `CollabCore` | P1 |
| **Zone Loading** | Stream zones based on player location | `WorldStreaming` | P1 |

```cpp
// TravelSystem Module
UCLASS()
class UTravelSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Initiate wormhole travel to destination zone
    UFUNCTION(BlueprintCallable)
    bool InitiateWormholeTravel(const FString& PlayerID, const FString& DestinationZoneID);
    
    // Get available travel destinations
    UFUNCTION(BlueprintCallable)
    TArray<FTravelDestination> GetAvailableDestinations(const FString& CurrentZoneID);
};

// CollabCore Module - Real-time Editing
UCLASS()
class UCollaborationSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Join collaborative lab session
    UFUNCTION(BlueprintCallable)
    bool JoinLabSession(const FString& PlayerID, const FString& LabID);
    
    // Broadcast edit to all collaborators
    UFUNCTION(BlueprintCallable)
    void BroadcastLabEdit(const FLabEditAction& Action);
    
    // Sync lab state from server
    UFUNCTION(BlueprintCallable)
    void SyncLabState(const FString& LabID);
};
```

#### Week 6-7: Economy & Trading

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Trading Post Marketplace** | Player-driven buy/sell system | `MarketplaceCore` | P1 |
| **Anomaly Detection** | Trade velocity checks, AI flagging for black markets | `SecurityCore` | P1 |
| **Order Matching Engine** | Match buy/sell orders efficiently | `MarketplaceCore` | P1 |

```cpp
// MarketplaceCore Module
UCLASS()
class UMarketplaceSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Create market order
    UFUNCTION(BlueprintCallable)
    FString CreateOrder(const FMarketOrder& Order);
    
    // Match orders and execute trades
    UFUNCTION(BlueprintCallable)
    TArray<FTradeExecution> MatchOrders(const FString& AssetType);
    
    // Get market listings
    UFUNCTION(BlueprintCallable)
    TArray<FMarketListing> GetListings(const FString& AssetType, EOrderType FilterType);
};
```

#### Week 7-8: Mech Challenges & Progression

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Mech Challenge Builder** | Physics-based construction system | `MechBuilder` | P1 |
| **Scoring System** | Efficiency/innovation metrics | `ChallengeCore` | P1 |
| **Multiplayer Judging Queue** | Queue system for challenge submissions | `ChallengeCore` | P1 |
| **Skill Trees** | Progression unlocks and specializations | `ProgressionCore` | P1 |
| **Credit Ledger** | Breakthrough credits distributed as Biocoin royalties | `BiocoinCore` | P1 |

```cpp
// ChallengeCore Module
UCLASS()
class UChallengeSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Submit mech for challenge
    UFUNCTION(BlueprintCallable)
    FString SubmitMechChallenge(const FString& PlayerID, const FMechSubmission& Submission);
    
    // Calculate score based on efficiency and innovation
    UFUNCTION(BlueprintCallable)
    FChallengeScore CalculateScore(const FMechSubmission& Submission);
    
    // Add to judging queue
    UFUNCTION(BlueprintCallable)
    void AddToJudgingQueue(const FString& SubmissionID);
};

// ProgressionCore Module
UCLASS()
class UProgressionSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Get player skill tree
    UFUNCTION(BlueprintCallable)
    FSkillTree GetSkillTree(const FString& PlayerID);
    
    // Unlock skill node
    UFUNCTION(BlueprintCallable)
    bool UnlockSkill(const FString& PlayerID, const FString& SkillNodeID);
    
    // Distribute breakthrough credits
    UFUNCTION(BlueprintCallable)
    void DistributeBreakthroughCredits(const FString& BreakthroughID, const TArray<FContributor>& Contributors);
};
```

---

### Could-Have (Expansion & Polish) — Weeks 9+

Polish, optimization, and expansion features for production readiness.

#### Week 9-10: Monetization & Governance Expansion

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Ad/Brand Integration** | In-game rewards tied to verified achievements | `AdSystem` | P2 |
| **Faction Systems** | Player factions with unique bonuses | `FactionCore` | P2 |
| **API Reputation Stakes** | Expand API access via reputation | `APIMarketplace` | P2 |

```cpp
// AdSystem Module
UCLASS()
class UAdRewardSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Verify achievement for ad reward eligibility
    UFUNCTION(BlueprintCallable)
    bool VerifyAchievementForReward(const FString& PlayerID, const FString& AchievementID);
    
    // Grant progression boost from ad interaction
    UFUNCTION(BlueprintCallable)
    void GrantAdReward(const FString& PlayerID, const FAdReward& Reward);
};

// FactionCore Module
UCLASS()
class UFactionSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
    
public:
    // Join faction
    UFUNCTION(BlueprintCallable)
    bool JoinFaction(const FString& PlayerID, const FString& FactionID);
    
    // Get faction bonuses
    UFUNCTION(BlueprintCallable)
    TArray<FFactionBonus> GetFactionBonuses(const FString& FactionID);
};
```

#### Week 10-11: Performance & Optimization

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Network Sync Optimizers** | Delta compression, prediction | `NetworkCore` | P2 |
| **Load Balancing** | Distribute player density across servers | `ServerInfra` | P2 |
| **LOD Management** | Dynamic level-of-detail for assets | `RenderingCore` | P2 |

#### Week 11-12: UI/UX Polish

| Task | Description | Module | Priority |
|------|-------------|--------|----------|
| **Holographic Collab Views** | 3D visualization for collaboration | `CollabUI` | P2 |
| **Lore Archive** | In-game encyclopedia and history | `LoreSystem` | P2 |
| **Mobile-Responsive Dashboards** | Cross-platform UI support | `UICore` | P2 |

---

### Development Workflow

#### GitHub Projects Integration

```
bioworld-development/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── must-have-task.md
│   │   ├── should-have-task.md
│   │   └── could-have-task.md
│   └── workflows/
│       ├── ci-tests.yml
│       └── copilot-review.yml
├── Projects/
│   ├── Core-Loop (Weeks 1-4)
│   ├── Multiplayer (Weeks 5-8)
│   └── Polish (Weeks 9+)
```

#### Copilot Test Generation

For each module, use Copilot to generate test scaffolding:

```cpp
// Example: BiocoinCore Tests (Copilot-assisted)
UCLASS()
class UBiocoinTests : public UAutomationTestBase
{
public:
    // Test 4x conversion rate
    void TestConversionRate()
    {
        float FiatAmount = 100.0f;
        int64 Expected = 400;
        int64 Result = BiocoinSubsystem->ConvertToBiocoin(FiatAmount);
        TestEqual("Conversion should be 4x", Result, Expected);
    }
    
    // Test account binding enforcement
    void TestAccountBinding()
    {
        FString TokenID = MintToken(PlayerA, 100);
        bool CanTransfer = AttemptTransfer(TokenID, PlayerA, PlayerB);
        TestFalse("Account-bound tokens should not transfer", CanTransfer);
    }
    
    // Test external transfer lockdown
    void TestExternalTransferBlock()
    {
        FString TokenID = MintToken(PlayerA, 100);
        bool ExternalAttempt = AttemptExternalExport(TokenID);
        TestFalse("External exports should be blocked", ExternalAttempt);
    }
};
```

#### Sprint Planning Template

| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| Sprint 1 | Account & Assets | Player auth, 10MB uploader, cloud storage |
| Sprint 2 | Lab Foundation | Lab class, placement, basic simulation |
| Sprint 3 | Biocoin Core | Minting, account-binding, governance voting |
| Sprint 4 | Core Loop Polish | Integration testing, bug fixes, prototype demo |
| Sprint 5 | Travel System | Wormhole travel, zone streaming |
| Sprint 6 | Collaboration | Real-time co-op editing via WebSockets |
| Sprint 7 | Marketplace | Trading post, anomaly detection |
| Sprint 8 | Challenges | Mech builder, scoring, judging queue |

---

### Module Dependency Graph

```
PlayerCore ──────┬──────► LabSystem ──────► SimulationCore
                 │              │
                 │              ▼
                 │        LabUI (Dashboard)
                 │
                 ▼
BiocoinCore ◄────┴──────► GovernanceCore
     │                          │
     ▼                          ▼
MarketplaceCore           GovernanceUI
     │
     ▼
SecurityCore (Anomaly Detection)
     │
     ▼
EnforcementSubsystem
```

---

### Quality Gates

Before moving to next phase:

| Phase | Gate Requirements |
|-------|-------------------|
| Must-Have → Should-Have | Core loop playable, Biocoin minting works, basic lab building functional |
| Should-Have → Could-Have | Multiplayer stable, marketplace operational, challenges scoreable |
| Could-Have → Release | Performance targets met, UI polish complete, security audited |
