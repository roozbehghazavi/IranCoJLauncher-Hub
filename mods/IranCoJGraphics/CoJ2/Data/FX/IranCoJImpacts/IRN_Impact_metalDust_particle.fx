ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.9)
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
		keyv4(0, 0.4, 0.4, 0.42, 0)
		keyv4(0.04, 0.4, 0.4, 0.42, 0.7)
		keyv4(0.35, 0.4, 0.4, 0.42, 0.5)
		keyv4(0.45, 0.4, 0.4, 0.42, 0.2)
		keyv4(0.9, 0.4, 0.4, 0.42, 0)
	}

	Size()
	{
		keyf(0, 10)
		keyf(0.2, 30)
		keyf(0.9, 65)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_ImpactDust_particleBLEND.mat", "IRN_ImpactDust_particleBLEND.mat")

	TexMultiRect(4, 4, 16)
	TexPlayMode("forward", 17.78)
}
