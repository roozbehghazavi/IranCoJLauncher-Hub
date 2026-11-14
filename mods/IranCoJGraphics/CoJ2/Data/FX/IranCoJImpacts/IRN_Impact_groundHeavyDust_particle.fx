ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.08)
	}

	GravityMul()
	{
		keyf(0, 0.05)
	}

	Drag()
	{
		keyf(0, 4)
	}

	WindInfluence()
	{
		keyf(0, 1)
	}

	Color()
	{
		keyv4(0, 0.58, 0.42, 0.3, 0)
		keyv4(0.04, 0.58, 0.42, 0.3, 0.7)
		keyv4(0.35, 0.58, 0.42, 0.3, 0.5)
		keyv4(0.54, 0.58, 0.42, 0.3, 0.2)
		keyv4(1.08, 0.58, 0.42, 0.3, 0)
	}

	Size()
	{
		keyf(0, 16)
		keyf(0.2, 48)
		keyf(1.08, 104)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_ImpactDust_particleBLEND.mat", "IRN_ImpactDust_particleBLEND.mat")

	TexMultiRect(4, 4, 16)
	TexPlayMode("forward", 14.81)
}
