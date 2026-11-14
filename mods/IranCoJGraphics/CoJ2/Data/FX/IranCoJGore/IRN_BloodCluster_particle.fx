ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.8)
	}

	GravityMul()
	{
		randf(0, 1.5, 2)
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
		keyv4(1.08, 0.55, 0.55, 0.55, 0.12)
		keyv4(1.8, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		keyf(0, 26)
		keyf(0.4, 32)
		keyf(1.8, 55)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodCluster_particleBLEND.mat", "IRN_BloodCluster_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
