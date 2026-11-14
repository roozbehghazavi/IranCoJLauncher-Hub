ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.35)
	}

	GravityMul()
	{
		keyf(0, 1)
	}

	Drag()
	{
		keyf(0, 1.2)
	}

	WindInfluence()
	{
		keyf(0, 0)
	}

	Color()
	{
		keyv4(0, 1, 0.9, 0.6, 1)
		keyv4(0.35, 1, 0.5, 0.15, 0)
	}

	Size()
	{
		keyv(0, 5, 0.04, 0)
	}

	Trail()

	Material("Spark_particleADD.mat", "Spark_particleADD.mat")
}
