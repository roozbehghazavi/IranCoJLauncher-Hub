ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.2)
	}

	GravityMul()
	{
		randf(0, 1, 1)
	}

	Drag()
	{
		randf(0, 0.05, 0.1)
	}

	Color()
	{
		keyv4(0, 0.8, 0.8, 0.8, 1)
		keyv4(1.2, 0.8, 0.8, 0.8, 0.95)
	}

	Size()
	{
		randf(0, 5, 8)
	}

	AspectRatio()
	{
		randf(0, 0.22, 0.28)
	}

	Material("IRN_BloodFall_particleBLEND.mat", "IRN_BloodFall_particleBLEND.mat")

	TexMultiRect(4, 1, 4)
	TexPlayMode("random_once", 1)
}
