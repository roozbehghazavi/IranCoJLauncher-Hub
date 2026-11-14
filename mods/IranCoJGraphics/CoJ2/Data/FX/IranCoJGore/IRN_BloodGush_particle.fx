ParticleDef()
{
	LifeTime()
	{
		keyf(0, 2.2)
	}

	GravityMul()
	{
		randf(0, 1, 1.4)
	}

	Drag()
	{
		randf(0, 1, 2)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 1)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.86)
		keyv4(0.272, 0.55, 0.55, 0.55, 0.5)
		keyv4(1.32, 0.55, 0.55, 0.55, 0.12)
		keyv4(2.2, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		keyf(0, 50)
		keyf(0.2, 58)
		keyf(2.5, 165)
	}

	Trail()

	Material("IRN_BloodGush_particleBLEND.mat", "IRN_BloodGush_particleBLEND.mat")

	TexMultiRect(4, 1, 4)
	TexPlayMode("random_once", 1)
}
